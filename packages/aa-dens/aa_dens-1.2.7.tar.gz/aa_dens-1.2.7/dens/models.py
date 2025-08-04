"""Models."""

import datetime
from typing import Optional

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from esi.models import Token
from eveuniverse.models import EvePlanet

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger

from dens.managers import (
    DenOwnerManager,
    MercenaryDenManager,
    MercernaryDenReinforcedNotificationManager,
)

ESI_SCOPES = [
    "esi-assets.read_assets.v1",
    "esi-characters.read_notifications.v1",
]

logger = get_extension_logger(__name__)


class General(models.Model):
    """A meta model for app permissions."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app"),
            (
                "corporation_view",
                "Can view all dens anchored by members of their corporation",
            ),
            (
                "alliance_view",
                "Can view all dens anchored by members of their alliance",
            ),
            ("manager", "Can see all user's mercenary dens"),
        )


class DenOwner(models.Model):
    """Represents a character that will drop mercenary dens"""

    objects = DenOwnerManager()

    character_ownership = models.ForeignKey(
        CharacterOwnership,
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Character used to sync mercenary dens",
    )

    is_enabled = models.BooleanField(
        default=True, db_index=True, help_text="Disabled characters won't be synced"
    )

    def __str__(self):
        return self.character_name

    def fetch_token(self) -> Token:
        """Return valid token for this mining corp or raise exception on any error."""
        if not self.character_ownership:
            raise RuntimeError("This owner has no character configured.")
        token = (
            Token.objects.filter(
                character_id=self.character_ownership.character.character_id
            )
            .require_scopes(ESI_SCOPES)
            .require_valid()
            .first()
        )
        if not token:
            raise Token.DoesNotExist(f"{self}: No valid token found.")
        return token

    @property
    def character_name(self) -> str:
        """Returns the character name"""
        return self.character_ownership.character.character_name

    @property
    def user_name(self) -> str:
        """Returns the user name"""
        return self.character_ownership.user.username

    @property
    def character_id(self) -> int:
        """Returns the character id"""
        return self.character_ownership.character.character_id

    def enable(self):
        """Sets an owner back to activity"""
        self.is_enabled = True
        self.save()

    def disable(self):
        """Disables an owner"""
        self.is_enabled = False
        self.save()


class MercenaryDen(models.Model):
    """Represents anchored mercenary dens"""

    objects = MercenaryDenManager()

    id = models.BigIntegerField(
        primary_key=True, help_text=_("Eve online id of the den")
    )

    owner = models.ForeignKey(
        DenOwner,
        on_delete=models.CASCADE,
        help_text=_("Character that anchored the den"),
    )
    location = models.OneToOneField(
        EvePlanet, on_delete=models.CASCADE, help_text=_("Location of the den")
    )

    def __str__(self) -> str:
        return f"Den {self.location.name}"

    @property
    def is_reinforced(self) -> bool:
        """True if there's an unexited reinforcement notification"""
        now = timezone.now()
        return MercenaryDenReinforcedNotification.objects.filter(
            den=self, exit_reinforcement__gt=now
        ).exists()

    @property
    def reinforcement_time(self) -> Optional[datetime.datetime]:
        """Return the den reinforcement time if it exists"""
        now = timezone.now()
        try:
            notification = MercenaryDenReinforcedNotification.objects.get(
                den=self, exit_reinforcement__gt=now
            )
            return notification.exit_reinforcement
        except MercenaryDenReinforcedNotification.DoesNotExist:
            pass
        return None


class MercenaryDenReinforcedNotification(models.Model):
    """Represents the notification of an owner den reinforced"""

    objects = MercernaryDenReinforcedNotificationManager()

    id = models.BigIntegerField(primary_key=True)

    den = models.ForeignKey(MercenaryDen, on_delete=models.SET_NULL, null=True)

    reinforced_by = models.ForeignKey(
        EveCharacter,
        on_delete=models.CASCADE,
        help_text="Character that reinforced the Mercenary Den",
    )
    enter_reinforcement = models.DateTimeField(
        help_text=_("Timer when the den was reinforced")
    )
    exit_reinforcement = models.DateTimeField(
        help_text=_("Timer when the den will leave reinforcement")
    )

    def __str__(self) -> str:
        return f"Den {self.den.location.name} reinforced by {self.reinforced_by.character_name}"

    def is_in_future(self) -> bool:
        """True if the timer is in the future"""
        return self.exit_reinforcement > timezone.now()
