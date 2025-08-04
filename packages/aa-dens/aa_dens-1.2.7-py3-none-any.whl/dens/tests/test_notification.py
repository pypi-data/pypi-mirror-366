import datetime
from copy import deepcopy

from structuretimers.models import Timer as StructureTimer

from django.test import TestCase
from django.utils import timezone
from eveuniverse.models import EveType

from allianceauth.eveonline.models import EveCharacter
from allianceauth.timerboard.models import Timer as TimerboardTimer

from dens.models import MercenaryDenReinforcedNotification
from dens.tests.utils import (
    NO_ALLIANCE_REINFORCE_NOTIFICATION,
    REINFORCE_NOTIFICATION,
    create_fake_den,
    create_fake_den_owner,
    create_fake_den_owner_no_alliance,
    create_fake_notification,
)

from ..tasks import DenMissingFromDatabase, create_reinforce_notification
from ..thirdparty.structuretimers import create_structuretimer_timer
from ..thirdparty.timerboard import create_timerboard_timer
from .testdata.load_eveuniverse import load_eveuniverse


class TestNotification(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()

    def test_parsing(self):

        res = MercenaryDenReinforcedNotification.objects.parse_information_from_notification(
            REINFORCE_NOTIFICATION
        )

        self.assertIsNotNone(res)

        self.assertEqual(res["aggressor_alliance"]["id"], "99003214")
        self.assertEqual(res["aggressor_alliance"]["name"], "Brave Collective")
        self.assertEqual(res["aggressor_corporation"]["id"], "98169165")
        self.assertEqual(res["aggressor_corporation"]["name"], "Brave Newbies Inc.")
        self.assertEqual(res["aggressor_character_id"], 96914524)
        self.assertEqual(res["planet_id"], 40255101)
        self.assertEqual(res["solar_system_id"], 30004028)
        self.assertEqual(res["timestamp_entered"], 133761583913385305)
        self.assertEqual(res["timestamp_exited"], 133762405913385305)

    def test_create_from_notification(self):

        owner = create_fake_den_owner()
        create_fake_den(owner)

        create_reinforce_notification(REINFORCE_NOTIFICATION)

        stored_reinforce_notification = (
            MercenaryDenReinforcedNotification.objects.all()[0]
        )

        self.assertIsNotNone(stored_reinforce_notification)

        self.assertEqual(stored_reinforce_notification.id, 2064665856)
        self.assertEqual(
            stored_reinforce_notification.reinforced_by,
            EveCharacter.objects.get_character_by_id(96914524),
        )

        self.assertTrue(
            timezone.is_aware(stored_reinforce_notification.enter_reinforcement)
        )
        self.assertTrue(
            timezone.is_aware(stored_reinforce_notification.exit_reinforcement)
        )

    def test_in_future(self):
        reinforce_notification = create_fake_notification()

        self.assertFalse(reinforce_notification.is_in_future())

        reinforce_notification.exit_reinforcement = timezone.now() + datetime.timedelta(
            days=1
        )
        reinforce_notification.save()

        self.assertTrue(reinforce_notification.is_in_future())

    def test_add_timerboard(self):
        reinforce_notification = create_fake_notification()

        self.assertEqual(TimerboardTimer.objects.count(), 0)

        create_timerboard_timer(reinforce_notification)

        self.assertEqual(TimerboardTimer.objects.count(), 1)

        timer = TimerboardTimer.objects.all()[0]

        self.assertEqual(timer.details, "Mercenary den reinforced by Butt Chili")
        self.assertEqual(timer.system, "E-VKJV")
        self.assertEqual(timer.planet_moon, "E-VKJV VI")
        self.assertEqual(timer.structure, TimerboardTimer.Structure.MERCDEN)
        self.assertEqual(timer.timer_type, TimerboardTimer.TimerType.FINAL)
        self.assertEqual(timer.objective, TimerboardTimer.Objective.FRIENDLY)
        self.assertEqual(timer.eve_time, reinforce_notification.exit_reinforcement)
        self.assertFalse(timer.important)
        self.assertIsNone(timer.eve_character)
        self.assertEqual(
            timer.eve_corp,
            reinforce_notification.den.owner.character_ownership.character.corporation,
        )
        self.assertFalse(timer.corp_timer)
        self.assertIsNone(timer.user)

    def test_add_structuretimer(self):
        reinforce_notification = create_fake_notification()

        self.assertEqual(StructureTimer.objects.count(), 0)

        create_structuretimer_timer(reinforce_notification)

        self.assertEqual(StructureTimer.objects.count(), 1)

        timer = StructureTimer.objects.all()[0]

        structure_type, _ = EveType.objects.get_or_create_esi(id=85230)

        self.assertEqual(timer.date, reinforce_notification.exit_reinforcement)
        self.assertIsNone(timer.details_image_url)
        self.assertEqual(timer.details_notes, "Reinforced by Butt Chili")
        # self.assertEqual(timer.eve_alliance, 99011247)
        self.assertEqual(
            timer.eve_character,
            reinforce_notification.den.owner.character_ownership.character,
        )
        self.assertEqual(
            timer.eve_corporation,
            reinforce_notification.den.owner.character_ownership.character.corporation,
        )
        self.assertEqual(
            timer.eve_solar_system, reinforce_notification.den.location.eve_solar_system
        )
        self.assertFalse(timer.is_important)
        self.assertFalse(timer.is_opsec)
        self.assertEqual(timer.location_details, "E-VKJV VI")
        self.assertEqual(timer.objective, StructureTimer.Objective.FRIENDLY)
        self.assertEqual(timer.owner_name, "Ji'had Rokym")
        self.assertEqual(timer.structure_type, structure_type)
        self.assertEqual(timer.structure_name, "VI")
        self.assertEqual(timer.timer_type, StructureTimer.Type.FINAL)
        self.assertIsNone(timer.user)
        self.assertEqual(timer.visibility, StructureTimer.Visibility.UNRESTRICTED)

    def test_add_structuretimer_without_alliance(self):
        owner = create_fake_den_owner_no_alliance()
        create_fake_den(owner)
        create_reinforce_notification(REINFORCE_NOTIFICATION)
        notification = MercenaryDenReinforcedNotification.objects.all()[0]

        create_structuretimer_timer(notification=notification)

    def test_bad_notification(self):
        """Test when a notification that doesn't have the correct format is passed"""
        reinforce_notification = {"text": "BAD INPUT"}

        self.assertRaises(
            ValueError,
            MercenaryDenReinforcedNotification.objects.create_from_notification,
            reinforce_notification,
        )

    def test_past_notification_not_existing_den(self):
        """Receives a past notification for a den no longer existing"""
        create_reinforce_notification(REINFORCE_NOTIFICATION)

        self.assertEqual(MercenaryDenReinforcedNotification.objects.count(), 1)

        stored_reinforce_notification = (
            MercenaryDenReinforcedNotification.objects.all()[0]
        )

        self.assertEqual(stored_reinforce_notification.id, 2064665856)
        self.assertEqual(
            stored_reinforce_notification.reinforced_by,
            EveCharacter.objects.get_character_by_id(96914524),
        )

        self.assertTrue(
            timezone.is_aware(stored_reinforce_notification.enter_reinforcement)
        )
        self.assertTrue(
            timezone.is_aware(stored_reinforce_notification.exit_reinforcement)
        )

        self.assertIsNone(stored_reinforce_notification.den)

    def test_future_notification_not_existing_den(self):
        """
        Receives a notification for a den not yet out of reinforcement but not yet in the database
        Should occur if a den is reffed after anchoring before an asset update triggered
        """
        json_notification = deepcopy(
            REINFORCE_NOTIFICATION
        )  # Seems like not copying will override the value in all tests
        # Changes exit time to 2056
        json_notification["text"] = (
            'aggressorAllianceName: <a href="showinfo:16159//99003214">Brave Collective</a>\naggressorCharacterID: 96914524\naggressorCorporationName: <a href="showinfo:2//98169165">Brave Newbies Inc.</a>\nitemID: &id001 1047210542765\nmercenaryDenShowInfoData:\n- showinfo\n- 85230\n- *id001\nplanetID: 40255101\nplanetShowInfoData:\n- showinfo\n- 11\n- 40255101\nsolarsystemID: 30004028\ntimestampEntered: 133761583913385305\ntimestampExited: 143762405913385305\ntypeID: 85230\n'
        )

        self.assertRaises(
            DenMissingFromDatabase, create_reinforce_notification, json_notification
        )

    def test_correctly_parses_when_aggressor_not_in_alliance(self):
        self.assertIsNotNone(
            MercenaryDenReinforcedNotification.objects.parse_information_from_notification(
                NO_ALLIANCE_REINFORCE_NOTIFICATION
            )
        )

    def test_notification_id002(self):
        """
        This notification failed to parse because some additionnal fields were present in the text.
        `&id002` and `*id002`
        """
        notification = {
            "is_read": True,
            "notification_id": 2101785272,
            "sender_id": 1000438,
            "sender_type": "corporation",
            "text": 'aggressorAllianceName: <a href="showinfo:16159//99012770">Black Rose.</a>\naggressorCharacterID: 1056152916\naggressorCorporationName: <a href="showinfo:2//98772518">Orbital Bloom</a>\nitemID: &id001 1047787968947\nmercenaryDenShowInfoData:\n- showinfo\n- 85230\n- *id001\nplanetID: &id002 40128505\nplanetShowInfoData:\n- showinfo\n- 11\n- *id002\nsolarsystemID: 30002015\ntimestampEntered: 133814418228106194\ntimestampExited: 133815271538106194\ntypeID: 85230\n',
            "timestamp": datetime.datetime(
                2025, 1, 15, 19, 10, tzinfo=datetime.timezone.utc
            ),
            "type": "MercenaryDenReinforced",
        }

        MercenaryDenReinforcedNotification.objects.create_from_notification(
            notification
        )

    def test_backslash_n_in_corp_name_notification(self):
        """
        Notifications returned from the ESI can have a \n in the text field that breaks the previous regex parsing.
        Switching to a yaml parser should have fixed the problem
        """

        notification = {
            "notification_id": 2094252961,
            "sender_id": 1000438,
            "sender_type": "corporation",
            "text": 'aggressorAllianceName: <a href="showinfo:16159//1900696668">The Initiative.</a>\naggressorCharacterID: 96104294\naggressorCorporationName: <a href="showinfo:2//98457033">United Mining and Hauling\n  Inc</a>\nitemID: &id001 1047702713146\nmercenaryDenShowInfoData:\n- showinfo\n- 85230\n- *id001\nplanetID: 40255900\nplanetShowInfoData:\n- showinfo\n- 11\n- 40255900\nsolarsystemID: 30004041\ntimestampEntered: 133803021282336070\ntimestampExited: 133803877282336070\ntypeID: 85230\n',
            "timestamp": datetime.datetime(
                2025, 1, 2, 14, 35, tzinfo=datetime.timezone.utc
            ),
            "type": "MercenaryDenReinforced",
            "is_read": None,
        }

        MercenaryDenReinforcedNotification.objects.create_from_notification(
            notification
        )

    def test_partial_text_notification(self):
        """Test when the notification has enough to be considered a yaml dict but missing some fields"""

        notification = deepcopy(REINFORCE_NOTIFICATION)
        notification["text"] = (  # timestamp fields removed
            'aggressorAllianceName: <a href="showinfo:16159//99003214">Brave Collective</a>\naggressorCharacterID: 96914524\naggressorCorporationName: <a href="showinfo:2//98169165">Brave Newbies Inc.</a>\nitemID: &id001 1047210542765\nmercenaryDenShowInfoData:\n- showinfo\n- 85230\n- *id001\nplanetID: 40255101\nplanetShowInfoData:\n- showinfo\n- 11\n- 40255101\nsolarsystemID: 30004028\n'
        )

        self.assertRaises(
            ValueError,
            MercenaryDenReinforcedNotification.objects.create_from_notification,
            notification,
        )
