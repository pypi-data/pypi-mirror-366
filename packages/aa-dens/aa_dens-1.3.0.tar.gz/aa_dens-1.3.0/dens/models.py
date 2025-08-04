"""Models."""

import datetime
from typing import Optional

import dhooks_lite

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from esi.models import Token
from eveuniverse.core.eveimageserver import type_icon_url
from eveuniverse.models import EvePlanet

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger

from dens.managers import (
    DenOwnerManager,
    DiscordWebhookManager,
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


class DiscordWebhook(models.Model):
    """Discord webhook to route notifications to"""

    objects = DiscordWebhookManager()

    webhook_url = models.CharField(
        max_length=255, unique=True, help_text=_("Webhook URL")
    )

    is_enabled = models.BooleanField(default=True)
    name = models.CharField(
        max_length=30, unique=True, help_text="Text to recognize the webhook"
    )

    # pylint: disable = too-many-positional-arguments, too-many-arguments
    def send_info(
        self,
        title: str,
        content: str,
        fields=None,
        author_name: str = None,
        author_icon_url: str = None,
    ):
        """Sends an information through the webhook"""
        embed = self._build_embed(
            title, content, 0x5CDBF0, fields, author_name, author_icon_url
        )
        self._send_through_webhook([embed])

    # pylint: disable = too-many-positional-arguments, too-many-arguments
    def send_alert(
        self,
        title: str,
        content: str,
        fields=None,
        author_name: str = None,
        author_icon_url: str = None,
    ):
        """Sends an alert through the webhook"""
        embed = self._build_embed(
            title, content, 0xFF5733, fields, author_name, author_icon_url
        )
        self._send_through_webhook([embed])

    def _build_webhook(self) -> dhooks_lite.Webhook:
        """Builds the discord webhook and returns it"""
        return dhooks_lite.Webhook(
            self.webhook_url,
            username="Den notification",
            avatar_url="https://gitlab.com/uploads/-/system/project/avatar/64868536/tents_1_.png",
        )

    def _send_through_webhook(self, embeds: list[dhooks_lite.Embed]):
        """Sends embeds through the webhook"""
        webhook = self._build_webhook()
        webhook.execute(embeds=embeds)

    # pylint: disable = too-many-positional-arguments, too-many-arguments
    def _build_embed(
        self,
        title: str,
        content: str,
        color: int,
        fields=None,
        author_name: str = None,
        author_icon_url: str = None,
    ) -> dhooks_lite.Embed:
        """Build a discord embedd and returns it"""

        formatted_fields = []
        if fields:
            for field in fields:
                formatted_fields.append(dhooks_lite.Field(field[0], str(field[1])))
        if not author_name:
            author_name = "AA-Dens"

        embed = dhooks_lite.Embed(
            author=dhooks_lite.Author(
                name=author_name,
                icon_url=author_icon_url,
            ),
            title=title,
            description=content,
            thumbnail=dhooks_lite.Thumbnail(type_icon_url(85230, size=128)),
            color=color,
            fields=formatted_fields,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            footer=dhooks_lite.Footer(
                "aa-dens",
            ),
        )

        return embed
