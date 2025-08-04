"""Esi related functions"""

import datetime

from django.utils import timezone
from esi.clients import EsiClientProvider
from esi.models import Token

from allianceauth.services.hooks import get_extension_logger

# from .models import DenOwner
from . import __version__, models

MERCENARY_DENS_TYPE_IDS = [
    85230,
    85980,
]
TEMPERATE_PLANET_TYPE_ID = 11


class MissingTokenError(Exception):
    """Raised when the token for this user isn't found"""


esi = EsiClientProvider(app_info_text=f"aa-dens v{__version__}")
logger = get_extension_logger(__name__)


def get_character_assets_from_esi(owner: "models.DenOwner") -> list[dict]:
    """Returns all character assets from the ESI"""
    logger.info("Fetching esi asset for user id %s", owner.id)

    try:
        assets = esi.client.Assets.get_characters_character_id_assets(
            character_id=owner.character_id,
            token=owner.fetch_token().valid_access_token(),
        ).results()
    except Token.DoesNotExist as e:
        logger.error("Missing ESI token for owner %s")
        raise MissingTokenError("Missing ESI token when fetching owner assets") from e

    logger.debug(assets)

    return assets


def get_owner_anchored_dens_from_esi(owner: "models.DenOwner") -> list[dict]:
    """Return all dens locations from the ESI"""

    den_assets = [
        asset
        for asset in get_character_assets_from_esi(owner)
        if asset["type_id"] in MERCENARY_DENS_TYPE_IDS
        and asset["location_type"] == "solar_system"
    ]

    return den_assets


def get_esi_asset_location(owner: "models.DenOwner", item_id: int) -> (int, int, int):
    """Returns the position of an item"""
    logger.info(
        "Fetching item id %s location from owner %s esi information", item_id, owner
    )

    try:
        position = esi.client.Assets.post_characters_character_id_assets_locations(
            character_id=owner.character_id,
            item_ids=[item_id],
            token=owner.fetch_token().valid_access_token(),
        ).result()[0]["position"]
    except Token.DoesNotExist as e:
        logger.error("Missing ESI token for owner %s")
        raise MissingTokenError(
            "Missing ESI token when fetching owner asset location"
        ) from e

    logger.debug(position)

    return position["x"], position["y"], position["z"]


def get_owner_notifications(owner: "models.DenOwner") -> list[dict]:
    """Returns notifications from an owner"""
    logger.info("Fetching notifications for den owner id %s", owner.id)

    try:
        notifications = esi.client.Character.get_characters_character_id_notifications(
            character_id=owner.character_id,
            token=owner.fetch_token().valid_access_token(),
        ).results()
    except Token.DoesNotExist as e:
        logger.error("Missing ESI token for owner %s")
        raise MissingTokenError(
            "Missing ESI token when fetching owner notifications"
        ) from e

    logger.debug(notifications)

    return notifications


def get_owner_mercenarydenreinforced_notifications_from_esi(
    owner: "models.DenOwner",
) -> list[dict]:
    """Returns only the `MercenaryDenReinforced` notifications from this owner"""

    return [
        notification
        for notification in get_owner_notifications(owner)
        if notification["type"] == "MercenaryDenReinforced"
    ]


def get_time_eve(dt: int) -> datetime.datetime:
    """
    Formula to parse ESI timestamps to datetime
    https://forums.eveonline.com/t/timestamp-format-in-notifications-by-esi/230395
    """
    microseconds = dt / 10
    seconds, microseconds = divmod(microseconds, 1000000)
    days, seconds = divmod(seconds, 86400)
    return datetime.datetime(1601, 1, 1, tzinfo=timezone.utc) + datetime.timedelta(
        days, seconds
    )
