from django.core.management import BaseCommand

from allianceauth.services.hooks import get_extension_logger

from dens.esi import get_owner_notifications
from dens.models import DenOwner

logger = get_extension_logger(__name__)


class Command(BaseCommand):
    """Debugging command returning a character notifications"""

    help = "Returns all the character notifications from the ESI"

    def add_arguments(self, parser):
        parser.add_argument("character_id", type=int)

    def handle(self, *args, **options):
        character_id = options["character_id"]
        print(
            f"Trying to retrieve all ESI notifications for character id {character_id}",
        )
        owner = DenOwner.objects.get(
            character_ownership__character__character_id=character_id
        )

        notifications = get_owner_notifications(owner)
        print("USER NOTIFICATIONS =========================================")
        print(notifications)
        print("============================================================")
