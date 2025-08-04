from unittest.mock import call, patch

from django.test import TestCase

from dens.esi import MissingTokenError
from dens.models import DenOwner
from dens.tasks import update_all_den_owners
from dens.tests.utils import create_fake_den_owners


class TestTasks(TestCase):
    """Tests for different tasks"""

    @patch("dens.tasks.get_owner_anchored_dens_from_esi")
    def test_owner_updates_after_error(self, get_owner_anchored_dens_from_esi_mock):
        """If an owner errors out because of a missing token the next owner should still be updated"""
        get_owner_anchored_dens_from_esi_mock.side_effect = [
            MissingTokenError(),
            [],
        ]

        owners = create_fake_den_owners(2)

        update_all_den_owners()

        self.assertEqual(get_owner_anchored_dens_from_esi_mock.call_count, 2)
        calls = [call(owners[0]), call(owners[1])]
        get_owner_anchored_dens_from_esi_mock.assert_has_calls(calls, any_order=True)

        self.assertEqual(DenOwner.objects.filter(is_enabled=False).count(), 1)
