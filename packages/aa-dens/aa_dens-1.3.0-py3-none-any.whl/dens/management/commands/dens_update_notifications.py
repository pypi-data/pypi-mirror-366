from django.core.management import BaseCommand

from allianceauth.services.hooks import get_extension_logger

from dens import tasks

logger = get_extension_logger(__name__)


class Command(BaseCommand):
    help = "Update all den owners notifications"

    def handle(self, *args, **kwargs):
        logger.info(
            "Initializing update of den owners' notifications from command line"
        )
        tasks.update_all_owners_notifications.delay()
