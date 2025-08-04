"""App settings."""

from django.conf import settings

from app_utils.app_settings import clean_setting

EXAMPLE_SETTING_ONE = getattr(settings, "EXAMPLE_SETTING_ONE", None)

DENS_ADMIN_NOTIFICATIONS_ENABLED = clean_setting(
    "DENS_ADMIN_NOTIFICATIONS_ENABLED", True
)
