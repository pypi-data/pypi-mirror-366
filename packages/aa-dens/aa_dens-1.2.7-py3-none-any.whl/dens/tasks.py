"""Tasks."""

from celery import group, shared_task

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from eveuniverse.constants import EveGroupId
from eveuniverse.core.evesdeapi import nearest_celestial
from eveuniverse.models import EvePlanet

import app_utils.allianceauth
from allianceauth.analytics.tasks import analytics_event
from allianceauth.notifications.models import Notification
from allianceauth.services.hooks import get_extension_logger
from app_utils.django import app_labels

from dens.app_settings import DENS_ADMIN_NOTIFICATIONS_ENABLED
from dens.esi import (
    TEMPERATE_PLANET_TYPE_ID,
    MissingTokenError,
    get_esi_asset_location,
    get_owner_anchored_dens_from_esi,
    get_owner_mercenarydenreinforced_notifications_from_esi,
)
from dens.models import DenOwner, MercenaryDen, MercenaryDenReinforcedNotification

logger = get_extension_logger(__name__)


class DenMissingFromDatabase(Exception):
    """Exception raised when the Den Associated with a notification can't be found in the datbaase"""


@shared_task
def update_all_den_owners():
    """Initiates an update of all enabled den owners"""
    enabled_den_owners = DenOwner.objects.enabled_owners()
    logger.info("Updating %s den owners", enabled_den_owners.count())

    task_list = []
    for owner in enabled_den_owners:
        task_list.append(update_owner_dens.si(owner.id))

    group(task_list).delay()


@shared_task
def update_owner_dens(owner_id: int):
    """Updates the mercenary dens anchored by this owner"""
    logger.info("Updating mercenary dens for owner id %s", owner_id)
    owner = DenOwner.objects.get(id=owner_id)

    try:
        dens_assets = get_owner_anchored_dens_from_esi(owner)
    except MissingTokenError as e:
        logger.error(
            "Missing token for owner %s when fetching assets. Disabling owner."
        )
        disable_owner_and_notify(owner)
        raise e

    current_ids_set = {den["item_id"] for den in dens_assets}

    stored_ids_set = MercenaryDen.objects.get_owner_dens_ids_set(owner)

    disappeared_dens_ids = stored_ids_set - current_ids_set
    disappeared_dens = MercenaryDen.objects.filter(id__in=disappeared_dens_ids)
    logger.debug("Deleting %d dens", disappeared_dens.count())
    disappeared_dens.delete()

    new_dens_ids = current_ids_set - stored_ids_set
    logger.debug("Creating %d new dens", len(new_dens_ids))
    new_dens_tasks = []
    for dens_asset in dens_assets:
        if dens_asset["item_id"] in new_dens_ids:
            create_den_tasks = create_mercenary_den.si(owner_id, dens_asset)
            new_dens_tasks.append(create_den_tasks)

    group(new_dens_tasks).delay()


@shared_task
def create_mercenary_den(owner_id: int, den_asset_dict: dict):
    """Creates a new mercenary den associated with this owner from the asset dictionary"""
    den_item_id = den_asset_dict["item_id"]
    logger.info("Creating den id %s for owner id %d", den_item_id, owner_id)
    logger.debug(den_asset_dict)
    owner = DenOwner.objects.get(id=owner_id)

    try:
        x, y, z = get_esi_asset_location(owner, den_item_id)
    except MissingTokenError as e:
        logger.error(
            "Missing ESI token for user %s when fetching asset location. Disabling owner."
        )
        disable_owner_and_notify(owner)
        raise e
    nearest_planet = nearest_celestial(
        den_asset_dict["location_id"], x, y, z, EveGroupId.PLANET
    )

    if not nearest_planet or nearest_planet.type_id != TEMPERATE_PLANET_TYPE_ID:
        raise RuntimeError(
            f"Couldn't find planet corresponding to den id {den_item_id}"
        )

    planet, _ = EvePlanet.objects.get_or_create_esi(id=nearest_planet.id)

    MercenaryDen.objects.create(owner, den_item_id, planet)


@shared_task
def update_all_owners_notifications():
    """Starts an owner update job for every owner"""
    owners = DenOwner.objects.enabled_owners()
    logger.info("Starting notifications update for %s owners", owners.count())
    jobs = []
    for owner in owners:
        jobs.append(update_owner_notifications.si(owner.id))

    group(jobs).delay()


@shared_task
def update_owner_notifications(owner_id: int):
    """Checks all notifications related to an owner and update new den reinforcement notifications"""
    logger.info("Updating notifications for owner id %s", owner_id)

    owner = get_object_or_404(DenOwner, id=owner_id)
    try:
        notifications = get_owner_mercenarydenreinforced_notifications_from_esi(owner)
    except MissingTokenError as e:
        logger.error(
            "Missing ESI token when fetching owner %s notifications. Disabling owner."
        )
        disable_owner_and_notify(owner)
        raise e

    for notification in notifications:
        if not MercenaryDenReinforcedNotification.objects.is_notification_id_known(
            notification["notification_id"]
        ):
            create_reinforce_notification.delay(notification)


@shared_task
def create_reinforce_notification(notification_json: dict):
    """Saves a reinforce notification from the ESI information"""
    logger.info("Creating a den reinforced notification from %s", notification_json)

    reinforce_notification = (
        MercenaryDenReinforcedNotification.objects.create_from_notification(
            notification_json
        )
    )

    if reinforce_notification is None:
        raise DenMissingFromDatabase(
            f"The den associated with notification {notification_json} couldn't be found"
        )

    if reinforce_notification.is_in_future():
        logger.info("Trying to add the timer to timerboards")

        application_labels = app_labels()
        if "timerboard" in application_labels:
            from dens.thirdparty.timerboard import create_timerboard_timer

            logger.debug("Timerboard detected")
            create_timerboard_timer(reinforce_notification)
            logger.info("Timer added to timerboard")

        if "structuretimers" in application_labels:
            from dens.thirdparty.structuretimers import create_structuretimer_timer

            logger.debug("Structruetimer detected")
            create_structuretimer_timer(reinforce_notification)
            logger.info("Timer added to structuretimers")

        if "aadiscordbot" in application_labels:
            from dens.thirdparty.aadiscordbot import (
                send_reinforced_notification_to_user,
            )

            logger.debug("aa-discordbot detected")
            send_reinforced_notification_to_user(reinforce_notification)
            logger.info("Sent the notification to the user through discordbot")
        else:
            logger.debug("No aa-discordbot defaulting to auth notification")
            Notification.objects.notify_user(
                user=reinforce_notification.den.owner.character_ownership.user,
                title=_("Mercenary Den reinforced"),
                message=_(
                    "Mercenary Den on %(location)s has been reinforced by %(name)s.\n"
                    "Will exit reinforcement at %(time)s."
                    % {
                        "location": reinforce_notification.den.location.name,
                        "name": reinforce_notification.reinforced_by.name,
                        "time": reinforce_notification.exit_reinforcement.isoformat(),
                    }
                ),
            )
            logger.info(
                "Sent the notification to the user through alliance auth notifications"
            )


def disable_owner_and_notify(owner: DenOwner):
    """
    Will disable an owner and try to notify a user using discord otherwise will use an alliance auth notification
    """
    logger.info("Disable den owner %s and sending disable notification to user", owner)

    owner.disable()

    if "aadiscordbot" in app_labels():
        from dens.thirdparty.aadiscordbot import send_disable_notification_to_user

        logger.debug("aa-discordbot detected")
        send_disable_notification_to_user(owner)
        logger.info("Sent the disable notification to the user through discordbot")
    else:
        logger.debug("No aa-discordbot, defaulting to auth notification")
        Notification.objects.notify_user(
            user=owner.character_ownership.user,
            title=_("Mercenary den owner disabled"),
            level=Notification.Level.WARNING,
            message=_(
                f"""Mercenary den owner {owner} has been disabled.
                "Add it back to enable services again."""
            ),
        )
        logger.info(
            "Sent the disable notification to the user through aa notifications"
        )

    if DENS_ADMIN_NOTIFICATIONS_ENABLED:
        app_utils.allianceauth.notify_admins(
            _("Mercenary Den owner disabled"),
            _(f"Mercenary Den owner {owner} has been disabled"),
        )


def send_analytics(label: str, value):
    """
    Send an analytics event
    """

    logger.info("Sending analytic %s with value %s", label, value)

    analytics_event(
        namespace="dens.analytics",
        task="send_daily_stats",
        label=label,
        value=value,
        event_type="Stats",
    )


@shared_task
def send_daily_analytics():
    """Sends analytic information to the AA GA instance"""
    logger.info("Starting the daily analytics task")

    count_owners = DenOwner.objects.count()
    count_dens = MercenaryDen.objects.count()

    send_analytics("den_owners", count_owners)
    send_analytics("mercenary_dens", count_dens)
