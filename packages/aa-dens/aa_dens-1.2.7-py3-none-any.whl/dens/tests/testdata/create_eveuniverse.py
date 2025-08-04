from django.test import TestCase
from eveuniverse.tools.testdata import ModelSpec, create_testdata

from . import test_data_filename


class CreateEveUniverseTestData(TestCase):
    def test_create_testdata(self):
        test_data_spec = [
            ModelSpec(
                "EvePlanet",
                ids=[
                    40255090,
                    40255092,
                    40255094,
                    40255096,
                    40255099,
                    40255101,
                    40255105,
                    40255125,
                ],
            ),
            ModelSpec(
                "EveType",
                ids=[
                    85230,
                ],
            ),
        ]
        create_testdata(test_data_spec, test_data_filename())
