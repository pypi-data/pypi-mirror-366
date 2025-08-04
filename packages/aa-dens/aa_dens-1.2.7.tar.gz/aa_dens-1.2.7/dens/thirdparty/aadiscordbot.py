"""
Interactions with the aa-discordbot application

https://github.com/Solar-Helix-Independent-Transport/allianceauth-discordbot
"""

from aadiscordbot.tasks import send_message
from discord import Embed

from dens.models import DenOwner, MercenaryDenReinforcedNotification


def basic_embed(title: str) -> Embed:
    """Returns a basic embed for the aa-den application"""

    e = Embed(
        title=title,
    )
    e.set_footer(
        text="aa-dens",
        icon_url="https://gitlab.com/uploads/-/system/project/avatar/64868536/tents_1_.png",
    )

    return e


def send_reinforced_notification_to_user(
    notification: MercenaryDenReinforcedNotification,
):
    """Sends a discord message a user warning that a mercenary den has been reinforced"""

    user = notification.den.owner.character_ownership.user

    e = basic_embed(
        title="Mercenary Den reinforced",
    )
    e.add_field(name="Location", value=notification.den.location.name)
    e.add_field(name="Reinforced by", value=notification.reinforced_by.character_name)
    e.add_field(
        name="Exit reinforcement", value=notification.exit_reinforcement.isoformat()
    )

    send_message(user=user, embed=e)


def send_disable_notification_to_user(owner: DenOwner):
    """Sends a discord message to a user warning that an owner has been disabled"""

    e = basic_embed(
        title="Mercenary Den owner disabled",
    )
    e.set_author(
        name=owner.character_name,
        icon_url=owner.character_ownership.character.portrait_url_64,
    )
    e.description = f"Your mercenary den owner {owner} is missing an ESI token and has been disabled"
