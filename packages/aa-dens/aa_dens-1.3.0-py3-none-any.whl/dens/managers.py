"""Managers."""

import re
from typing import Optional

import yaml

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max, Q
from django.utils import timezone
from eveuniverse.models import EvePlanet

from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)
from allianceauth.services.hooks import get_extension_logger

from dens.esi import get_time_eve

from . import models as den_models

logger = get_extension_logger(__name__)


class DenOwnerManager(models.Manager):
    """Manager for DenOwner"""

    def enabled_owners(self):
        """Returns all active den owners"""
        return self.filter(is_enabled=True)


class MercenaryDenManager(models.Manager):
    """Manager for mercenary dens"""

    def get_queryset(self):
        """Overrides the default django queryset"""
        return MercenaryDenQuerySet(self.model, using=self._db)

    def get_owner_dens_ids_set(self, owner: "den_models.DenOwner") -> set[int]:
        """Returns a set with the id of all dens anchored by this owner"""
        return set(self.filter(owner=owner).values_list("id", flat=True))

    def create(
        self, owner: "den_models.DenOwner", den_id: int, location: EvePlanet, **kwargs
    ):
        """Creates a mercenary den and returns it"""
        if self.filter(location=location).exists():
            # Cleans a previous den that was probably the leftover of a disabled owner
            self.get(location=location).delete()
        return super().create(owner=owner, id=den_id, location=location, **kwargs)

    def filter_alliance_dens(self, alliance: EveAllianceInfo):
        """Returns all mercenary dens from owners in the given alliance"""
        return self.filter(
            owner__character_ownership__character__alliance_id=alliance.alliance_id
        )

    def filter_corporation_dens(self, corporation: EveCorporationInfo):
        """Returns all mercenary dens from owners in a given corporation"""
        return self.filter(
            owner__character_ownership__character__corporation_id=corporation.corporation_id
        )

    def filter_user_dens(self, user: User):
        """Return all mercenary dens associated with a user"""
        return self.filter(owner__character_ownership__user=user)

    def filter_is_reinforced(self, is_reinforced=True):
        """Filters by reinforcement"""
        return self.get_queryset().filter_is_reinforced(is_reinforced)


class MercenaryDenQuerySet(models.QuerySet):
    """Custom queryset for mercenary dens"""

    def filter_is_reinforced(self, is_reinforced=True):
        """Filters by reinforcement"""
        now = timezone.now()
        q = self.annotate(
            reinforce=Max("mercenarydenreinforcednotification__exit_reinforcement")
        ).values("id", "reinforce")
        if is_reinforced:
            q = q.filter(reinforce__gt=now)
        else:
            q = q.filter(Q(reinforce__lt=now) | Q(reinforce__isnull=True))
        return self.filter(id__in=q.values("id"))


class MercernaryDenReinforcedNotificationManager(models.Manager):
    """Manager for MercenaryDenReinforcedNotification"""

    def is_notification_id_known(self, notification_id: int) -> bool:
        """Will check if the notification id is in the database"""
        return self.filter(id=notification_id).exists()

    def parse_information_from_notification(self, notification_dict: dict) -> dict:
        """Generates and saves a new notification from the notification dict of the ESI"""

        text = yaml.load(notification_dict["text"], Loader=yaml.Loader)

        if not isinstance(text, dict):  # input string wasn't formatted correctly
            logger.error(
                "Couldn't make a notification out of %s the format doesn't seem like valid yaml",
                notification_dict,
            )
            raise ValueError(
                f"Couldn't make a notification out of {notification_dict} the format doesn't seem like valid yaml"
            )

        alliance_match = re.match(
            r"<a href=\"showinfo:16159//(?P<alliance_id>.+)\">(?P<alliance_name>.+)</a>",
            text["aggressorAllianceName"],
        )
        corporation_match = re.match(
            r"<a href=\"showinfo:2//(?P<corporation_id>.+)\">(?P<corporation_name>.+)</a>",
            text["aggressorCorporationName"],
        )

        try:
            return {
                "aggressor_character_id": text["aggressorCharacterID"],
                "planet_id": text["planetShowInfoData"][2],
                "timestamp_entered": text["timestampEntered"],
                "timestamp_exited": text["timestampExited"],
                "aggressor_alliance": (
                    {
                        "name": alliance_match.group("alliance_name"),
                        "id": alliance_match.group("alliance_id"),
                    }
                    if alliance_match
                    else None
                ),
                "aggressor_corporation": {
                    "name": corporation_match.group("corporation_name"),
                    "id": corporation_match.group("corporation_id"),
                },
                "solar_system_id": text["solarsystemID"],
                "mercenary_den_id": text["mercenaryDenShowInfoData"],
            }
        except KeyError as e:  # Missing fields
            logger.error(
                "Couldn't make a notification out of %s some field is missing: %s",
                notification_dict,
                e,
            )
            raise ValueError(
                f"Couldn't make a notification out of {notification_dict} some field is missing: {e}"
            ) from e

    def create_from_notification(
        self, notification: dict
    ) -> Optional["den_models.MercenaryDenReinforcedNotification"]:
        """
        Creates a den reinforced notification from an ESI notification.
        """

        notification_information = self.parse_information_from_notification(
            notification
        )
        if notification_information is None:
            logger.error("Couldn't make a notification out of %s", notification)
            raise ValueError(f"Couldn't make a notification out of {notification}")

        associated_planet, _ = EvePlanet.objects.get_or_create_esi(
            id=notification_information["planet_id"]
        )

        eve_character_id = notification_information["aggressor_character_id"]
        reinforced_by = EveCharacter.objects.get_character_by_id(eve_character_id)
        if reinforced_by is None:
            reinforced_by = EveCharacter.objects.create_character(eve_character_id)
        logger.debug("Reinforced by %s", reinforced_by)
        entered_reinforce = get_time_eve(notification_information["timestamp_entered"])
        exited_reinforce = get_time_eve(notification_information["timestamp_exited"])

        try:
            associated_den = den_models.MercenaryDen.objects.get(
                location=associated_planet
            )
        except den_models.MercenaryDen.DoesNotExist:
            logger.info(
                "Trying to parse the notification of a non existing den on planet id %s",
                associated_planet.id,
            )
            if (
                exited_reinforce > timezone.now()
            ):  # Future notification of unknown den, will need to reparse it
                return None
            associated_den = None  # Past notification, can be safely ignored

        notification = self.create(
            id=notification["notification_id"],
            den=associated_den,
            reinforced_by=reinforced_by,
            enter_reinforcement=entered_reinforce,
            exit_reinforcement=exited_reinforce,
        )

        return notification


class DiscordWebhookManager(models.Manager):
    """Custom DiscordWebhook Manager"""

    def active_webhooks(self):
        """Return active discord webhooks"""
        return self.filter(is_enabled=True)
