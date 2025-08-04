from django.test import TestCase

from dens import tasks
from dens.esi import MissingTokenError
from dens.models import DenOwner, MercenaryDen
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

    def test_enabled_owners(self):
        all_owners = DenOwner.objects.enabled_owners()
        self.assertEqual(2, all_owners.count())
        all_owners = list(all_owners)

        all_owners[0].disable()

        enabled_owners = DenOwner.objects.enabled_owners()
        self.assertEqual(1, enabled_owners.count())
        self.assertIn(all_owners[1], enabled_owners)

    def test_owner_gets_disabled(self):
        """Tests all functions that can disable owners to ensure they get disabled and MissingToken is raised"""

        owner = DenOwner.objects.all()[0]

        self.assertRaises(MissingTokenError, tasks.update_owner_dens, owner.id)
        owner = DenOwner.objects.get(id=owner.id)
        self.assertFalse(owner.is_enabled)

        owner.enable()
        self.assertTrue(owner.is_enabled)

        self.assertRaises(
            MissingTokenError, tasks.create_mercenary_den, owner.id, {"item_id": 123}
        )
        owner = DenOwner.objects.get(id=owner.id)
        self.assertFalse(owner.is_enabled)

        owner.enable()
        self.assertTrue(owner.is_enabled)

        self.assertRaises(MissingTokenError, tasks.update_owner_notifications, owner.id)
        owner = DenOwner.objects.get(id=owner.id)
        self.assertFalse(owner.is_enabled)

    def test_new_den_on_disabled_owner_planet(self):
        """Checks what happens when a new den is created on a planet with a disabled owner's den"""
        EVE_PLANET = 40255090

        owners = list(DenOwner.objects.all())

        owners[0].disable()

        self.assertEqual(2, MercenaryDen.objects.filter(owner=owners[0]).count())
        self.assertTrue(
            MercenaryDen.objects.filter(
                location_id=EVE_PLANET, owner=owners[0]
            ).exists()
        )

        create_fake_dens_for_owner(owners[1], [EVE_PLANET])

        self.assertEqual(1, MercenaryDen.objects.filter(location=EVE_PLANET).count())
