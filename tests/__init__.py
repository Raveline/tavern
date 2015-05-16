import unittest
import tavern.utils.bus as bus
from tavern.receivers.navigators import Selection
from tavern.world.world import Tavern
from tavern.world.customers import Customers
from tavern.world.map_commands import BuildCommand, PutCommand, RoomCommand
from tavern.world.actions import door, counter, chair


class TavernTest(unittest.TestCase):
    TEST_WORLD_WIDTH = 100
    TEST_WORLD_HEIGHT = 120

    def setUp(self):
        self.tavern = Tavern(TavernTest.TEST_WORLD_WIDTH,
                             TavernTest.TEST_WORLD_HEIGHT)
        self.tavern_map = self.tavern.tavern_map
        bus.bus.subscribe(self.tavern, bus.WORLD_EVENT)
        bus.bus.subscribe(self.tavern, bus.CUSTOMER_EVENT)
        self.customers = Customers(self.tavern)
        self.bootstrap()

    def bootstrap(self):
        def build_area(x, y, x2, y2):
            area = Selection(x, y)
            area.x2 = x2
            area.y2 = y2
            return area
        # Build a storage area
        commands = []
        commands.append(BuildCommand(build_area(2, 2, 5, 5)))
        # build a corridor to a tavern room
        commands.append(BuildCommand(build_area(5, 3, 9, 4)))
        commands.append(PutCommand(build_area(8, 3, 8, 4), door))
        # Build the tavern room
        commands.append(BuildCommand(build_area(9, 2, 12, 12)))
        commands.append(PutCommand(build_area(11, 1, 11, 1), door))
        for command in commands:
            bus.bus.publish({'command': command}, bus.WORLD_EVENT)
        commands = []
        commands.append(RoomCommand(self.tavern.tavern_map.fill_from(3, 3), 1))
        commands.append(RoomCommand(
            self.tavern.tavern_map.fill_from(10, 10), 0))
        commands.append(PutCommand(build_area(9, 11, 9, 11), counter))
        commands.append(PutCommand(build_area(9, 6, 9, 6), chair))
        for command in commands:
            bus.bus.publish({'command': command}, bus.WORLD_EVENT)
        print(self.tavern.tavern_map.tiles[11][9].wall)

    def tick_for(self, l=1):
        for i in range(1, l + 1):
            self.tavern.tick()
