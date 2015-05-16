from tests import TavernTest


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
