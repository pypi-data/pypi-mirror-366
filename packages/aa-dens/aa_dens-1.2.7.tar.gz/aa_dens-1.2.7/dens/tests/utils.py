import datetime

from dateutil.tz import tzutc

from eveuniverse.models import EvePlanet

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveAllianceInfo, EveCorporationInfo
from app_utils.testing import create_fake_user

from dens.models import DenOwner, MercenaryDen, MercenaryDenReinforcedNotification
from dens.tasks import create_reinforce_notification

REINFORCE_NOTIFICATION = {
    "is_read": True,
    "notification_id": 2064665856,
    "sender_id": 1000438,
    "sender_type": "corporation",
    "text": 'aggressorAllianceName: <a href="showinfo:16159//99003214">Brave Collective</a>\naggressorCharacterID: 96914524\naggressorCorporationName: <a href="showinfo:2//98169165">Brave Newbies Inc.</a>\nitemID: &id001 1047210542765\nmercenaryDenShowInfoData:\n- showinfo\n- 85230\n- *id001\nplanetID: 40255101\nplanetShowInfoData:\n- showinfo\n- 11\n- 40255101\nsolarsystemID: 30004028\ntimestampEntered: 133761583913385305\ntimestampExited: 133762405913385305\ntypeID: 85230\n',
    "timestamp": datetime.datetime(2024, 11, 15, 15, 33, tzinfo=tzutc()),
    "type": "MercenaryDenReinforced",
}

NO_ALLIANCE_REINFORCE_NOTIFICATION = {
    "is_read": True,
    "notification_id": 2064898731,
    "sender_id": 1000438,
    "sender_type": "corporation",
    "text": 'aggressorAllianceName: Unknown\naggressorCharacterID: 185018643\naggressorCorporationName: <a href="showinfo:2//828783563">exiles.</a>\nitemID: &id001 1047212774639\nmercenaryDenShowInfoData:\n- showinfo\n- 85230\n- *id001\nplanetID: 40255101\nplanetShowInfoData:\n- showinfo\n- 11\n- 40256161\nsolarsystemID: 30004045\ntimestampEntered: 133761878739722751\ntimestampExited: 133762846589722751\ntypeID: 85230\n',
    "timestamp": datetime.datetime(2024, 11, 15, 23, 45, tzinfo=datetime.timezone.utc),
    "type": "MercenaryDenReinforced",
}


def create_fake_den_owner() -> DenOwner:
    """Returns a fake den owner for test purposes"""

    user = create_fake_user(
        character_name="Ji'had Rokym",
        character_id=2119057263,
        corporation_id=98609038,
        corporation_ticker="ROKYM",
        corporation_name="Rokym's managment organisation",
        alliance_name="Tocards Professionnels",
        alliance_id=99011247,
    )

    char_ownership, _ = CharacterOwnership.objects.get_or_create(
        character=user.profile.main_character, user=user, owner_hash="fake_hash"
    )

    owner = DenOwner.objects.create(character_ownership=char_ownership)

    return owner


def create_fake_den_owner_no_alliance() -> DenOwner:
    """Returns a fake den owner not in an alliance"""

    user = create_fake_user(
        character_name="Ji'had Rokym",
        character_id=2119057263,
        corporation_id=98609038,
        corporation_ticker="ROKYM",
        corporation_name="Rokym's managment organisation",
    )

    char_ownership, _ = CharacterOwnership.objects.get_or_create(
        character=user.profile.main_character, user=user, owner_hash="fake_hash"
    )

    owner = DenOwner.objects.create(character_ownership=char_ownership)

    return owner


def create_fake_den_owners(number: int) -> list[DenOwner]:
    """Create as many den owners as needed all in their individual corporations and alliances"""

    owners = []
    for i in range(number):
        user = create_fake_user(
            character_name=f"User {i}",
            character_id=1000 + i,
            corporation_name=f"Corporation {i}",
            corporation_ticker=f"CORP{i}",
            corporation_id=2000 + i,
            alliance_name=f"Alliance {i}",
            alliance_id=3000 + i,
        )

        eve_alliance = EveAllianceInfo.objects.create(
            alliance_id=3000 + i,
            alliance_name=f"Alliance {i}",
            alliance_ticker=f"ALLY{i}",
            executor_corp_id=2000 + i,
        )
        EveCorporationInfo.objects.create(
            corporation_id=2000 + i,
            corporation_name=f"Corporation{i}",
            corporation_ticker=f"CORP{i}",
            member_count=1,
            alliance=eve_alliance,
        )

        char_ownership, _ = CharacterOwnership.objects.get_or_create(
            character=user.profile.main_character, user=user, owner_hash=f"fake_hash{i}"
        )

        owners.append(DenOwner.objects.create(character_ownership=char_ownership))

    return owners


def create_fake_den(owner: DenOwner) -> MercenaryDen:
    """Create a fake den belonging to the passed owner for test purposes"""

    planet_id = 40255101
    planet = EvePlanet.objects.get(id=planet_id)

    den = MercenaryDen.objects.create(owner=owner, den_id=1, location=planet)

    return den


def create_fake_dens_for_owner(
    owner: DenOwner, planet_ids: list[int]
) -> list[MercenaryDen]:
    """Create mercenary dens on the selected planets for the given owner"""
    existing_dens = MercenaryDen.objects.count()
    dens = []

    for i in range(len(planet_ids)):
        planet_id = planet_ids[i]
        planet = EvePlanet.objects.get(id=planet_id)
        dens.append(
            MercenaryDen.objects.create(
                owner=owner, location=planet, den_id=existing_dens + i
            )
        )

    return dens


def create_fake_notification():
    """Creates user, den and stores a den reinforcement notification"""
    owner = create_fake_den_owner()
    create_fake_den(owner)

    create_reinforce_notification(REINFORCE_NOTIFICATION)

    return MercenaryDenReinforcedNotification.objects.all()[0]
