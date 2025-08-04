"""
Handles interactions with the timerboard application

https://allianceauth.readthedocs.io/en/v4.6.1/features/apps/timerboard.html
"""

from allianceauth.eveonline.models import EveCorporationInfo
from allianceauth.timerboard.models import Timer

from dens.models import MercenaryDenReinforcedNotification


def create_timerboard_timer(notification: MercenaryDenReinforcedNotification):
    """
    Creates a timer for this reinforcement in the timerboard app
    """

    try:
        eve_corp = notification.den.owner.character_ownership.character.corporation
    except EveCorporationInfo.DoesNotExist:
        eve_corp = EveCorporationInfo.objects.create_corporation(
            notification.den.owner.character_ownership.character.corporation_id
        )

    Timer.objects.create(
        details=f"Mercenary den reinforced by {notification.reinforced_by.character_name}",
        system=notification.den.location.eve_solar_system.name,
        planet_moon=notification.den.location.name,
        structure=Timer.Structure.MERCDEN,
        timer_type=Timer.TimerType.FINAL,
        objective=Timer.Objective.FRIENDLY,
        eve_time=notification.exit_reinforcement,
        eve_corp=eve_corp,
    )
