from django.core.management import BaseCommand

from allianceauth.services.hooks import get_extension_logger

from dens.esi import get_character_assets_from_esi
from dens.models import DenOwner

logger = get_extension_logger(__name__)


class Command(BaseCommand):
    """Debugging command returning a character assets"""

    help = "Returns all the character assets from the ESI"

    def add_arguments(self, parser):
        parser.add_argument("character_id", type=int)

    def handle(self, *args, **options):
        character_id = options["character_id"]
        print(
            f"Trying to retrieve all ESI assets for user id {character_id}",
        )
        owner = DenOwner.objects.get(
            character_ownership__character__character_id=character_id
        )

        assets = get_character_assets_from_esi(owner)
        print("USER ASSETS ================================================")
        print(assets)
        print("============================================================")
