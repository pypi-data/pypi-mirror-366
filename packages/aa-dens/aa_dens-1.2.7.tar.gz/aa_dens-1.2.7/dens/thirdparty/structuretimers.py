"""
Handles interactions with the structuretimers application

https://gitlab.com/ErikKalkoken/aa-structuretimers
"""

from structuretimers.models import Timer

from eveuniverse.models import EveType

from allianceauth.eveonline.models import EveAllianceInfo, EveCorporationInfo

from dens.models import MercenaryDenReinforcedNotification


def create_structuretimer_timer(notification: MercenaryDenReinforcedNotification):
    """
    Creates a timer for this reinforcement in the structruretimer app
    """

    eve_character = notification.den.owner.character_ownership.character
    try:
        eve_corp = eve_character.corporation
    except EveCorporationInfo.DoesNotExist:
        eve_corp = EveCorporationInfo.objects.create_corporation(
            notification.den.owner.character_ownership.character.corporation_id
        )

    try:
        eve_alliance = eve_corp.alliance
    except EveAllianceInfo.DoesNotExist:
        eve_alliance = EveAllianceInfo.objects.create_alliance(eve_corp.alliance_id)

    structure_type, _ = EveType.objects.get_or_create_esi(id=85230)

    Timer.objects.create(
        date=notification.exit_reinforcement,
        details_notes=f"Reinforced by {notification.reinforced_by.character_name}",
        eve_alliance=eve_alliance,
        eve_character=eve_character,
        eve_corporation=eve_corp,
        eve_solar_system=notification.den.location.eve_solar_system,
        location_details=notification.den.location.name,
        objective=Timer.Objective.FRIENDLY,
        owner_name=eve_character.character_name,
        structure_type=structure_type,
        structure_name=notification.den.location.name.split()[-1],
        timer_type=Timer.Type.FINAL,
    )
