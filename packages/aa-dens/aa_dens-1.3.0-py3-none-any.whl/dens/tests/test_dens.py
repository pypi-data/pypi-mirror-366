from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)

from dens.models import DenOwner, MercenaryDen, MercenaryDenReinforcedNotification
from dens.tests.testdata.load_eveuniverse import load_eveuniverse
from dens.tests.utils import create_fake_den_owners, create_fake_dens_for_owner


class TestNotification(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()

        owners = create_fake_den_owners(2)

        create_fake_dens_for_owner(owners[0], [40255090, 40255092])
        create_fake_dens_for_owner(owners[1], [40255094])

    def test_pre_conditions(self):
        """Test case to check that the situations is as expected"""
        self.assertEqual(DenOwner.objects.count(), 2)
        self.assertEqual(MercenaryDen.objects.count(), 3)

        self.assertTrue(EveCorporationInfo.objects.filter(corporation_id=2000).exists())
        self.assertTrue(EveCorporationInfo.objects.filter(corporation_id=2001).exists())

        self.assertTrue(EveAllianceInfo.objects.filter(alliance_id=3000).exists())
        self.assertTrue(EveAllianceInfo.objects.filter(alliance_id=3001).exists())

    def test_get_all_dens(self):
        self.assertEqual(MercenaryDen.objects.all().count(), 3)

    def test_get_alliance_dens(self):
        alliance_1 = EveAllianceInfo.objects.get(alliance_id=3000)
        alliance_2 = EveAllianceInfo.objects.get(alliance_id=3001)

        self.assertEqual(
            MercenaryDen.objects.filter_alliance_dens(alliance_1).count(), 2
        )
        self.assertEqual(
            MercenaryDen.objects.filter_alliance_dens(alliance_2).count(), 1
        )

    def test_get_corporation_dens(self):
        corporation_1 = EveCorporationInfo.objects.get(corporation_id=2000)
        corporation_2 = EveCorporationInfo.objects.get(corporation_id=2001)

        self.assertEqual(
            MercenaryDen.objects.filter_corporation_dens(corporation_1).count(), 2
        )
        self.assertEqual(
            MercenaryDen.objects.filter_corporation_dens(corporation_2).count(), 1
        )

    def test_reinforce_filter(self):
        char = EveCharacter.objects.all()[0]
        now = timezone.now()
        dens = MercenaryDen.objects.all()

        # future den timer
        MercenaryDenReinforcedNotification.objects.create(
            id=2,
            den=dens[0],
            reinforced_by=char,
            enter_reinforcement=now - timedelta(hours=1),
            exit_reinforcement=now + timedelta(days=1),
        )
        # passed den timer
        MercenaryDenReinforcedNotification.objects.create(
            id=1,
            den=dens[1],
            reinforced_by=char,
            enter_reinforcement=now - timedelta(days=2),
            exit_reinforcement=now - timedelta(days=1),
        )
        # one den has no timers

        reinforce_true = MercenaryDen.objects.filter_is_reinforced(True)
        reinforce_false = MercenaryDen.objects.filter_is_reinforced(False)

        self.assertEqual(reinforce_true.count(), 1)
        self.assertEqual(reinforce_false.count(), 2)

        self.assertIn(dens[0], reinforce_true)
        self.assertIn(dens[1], reinforce_false)
        self.assertIn(dens[2], reinforce_false)
