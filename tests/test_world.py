from tests import TavernTest
from tavern.world.objects.functions import Functions
from tavern.world.actions import chair


class TestWorld(TavernTest):
    def test_world_size(self):
        """New tavern should be a rectangle, with the size
        given as parameters."""
        self.assertEqual(self.tavern_map.width, TavernTest.TEST_WORLD_WIDTH)
        self.assertEqual(self.tavern_map.height, TavernTest.TEST_WORLD_HEIGHT)
        self.assertEqual(len(self.tavern_map.tiles),
                         TavernTest.TEST_WORLD_HEIGHT)
        self.assertEqual(len(self.tavern_map.tiles[0]),
                         TavernTest.TEST_WORLD_WIDTH)

    def test_world_add_creatures(self):
        self.assertEqual(len(self.tavern.creatures), 1,
                         'The tavern should be empty at the beginning, but '
                         'for the Publican.')
        self.customers.make_customer()
        self.assertEqual(len(self.tavern.creatures), 2,
                         'Adding a customer should make a change in the world'
                         ' creatures list.')

    def test_adding_services(self):
        self.assertEqual(
            len(self.tavern_map.available_services[Functions.SITTING]),
            0,
            'The new tavern should not have available services.'
        )
        self.add_object(chair, 9, 6)
        self.assertEqual(
            len(self.tavern_map.available_services[Functions.SITTING]),
            1,
            'The new tavern should now have one available service.'
        )
