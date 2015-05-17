import unittest
from collections import defaultdict

import tavern.utils.bus as bus
from tavern.receivers.navigators import Selection
from tavern.world.world import Tavern
from tavern.world.customers import Customers
from tavern.world.map_commands import BuildCommand, PutCommand, RoomCommand
from tavern.world.actions import door, counter


class TavernTest(unittest.TestCase):
    TEST_WORLD_WIDTH = 100
    TEST_WORLD_HEIGHT = 120

    COUNTER_X = 9
    COUNTER_Y = 11

    def setUp(self):
        self.tavern = Tavern(TavernTest.TEST_WORLD_WIDTH,
                             TavernTest.TEST_WORLD_HEIGHT)
        self.tavern_map = self.tavern.tavern_map
        bus.bus.subscribe(self.tavern, bus.WORLD_EVENT)
        bus.bus.subscribe(self.tavern, bus.CUSTOMER_EVENT)
        self.customers = Customers(self.tavern)
        self.bootstrap()
        self.received_events = defaultdict(list)
        bus.bus.subscribe(self, bus.STATUS_EVENT)

    def receive(self, event):
        self.received_events[event.get('type')].append(event.get('data'))

    def assertReceived(self, event_type, description):
        self.assertIn(description, self.received_events[event_type])

    def _build_area(self, x, y, x2=None, y2=None):
        area = Selection(x, y)
        if x2 is None:
            x2 = x
        if y2 is None:
            y2 = y
        area.x2 = x2
        area.y2 = y2
        return area

    def bootstrap(self):
        # Build a storage area
        commands = []
        commands.append(BuildCommand(self._build_area(2, 2, 5, 5)))
        # build a corridor to a tavern room
        commands.append(BuildCommand(self._build_area(5, 3, 9, 4)))
        commands.append(PutCommand(self._build_area(8, 3, 8, 4), door))
        # Build the tavern room
        commands.append(BuildCommand(self._build_area(9, 2, 12, 12)))
        commands.append(PutCommand(self._build_area(11, 1, 11, 1), door))
        for command in commands:
            bus.bus.publish({'command': command}, bus.WORLD_EVENT)
        commands = []
        commands.append(RoomCommand(self.tavern.tavern_map.fill_from(3, 3), 1))
        commands.append(RoomCommand(
            self.tavern.tavern_map.fill_from(10, 10), 0))
        commands.append(PutCommand(self._build_area(TavernTest.COUNTER_X,
                                                    TavernTest.COUNTER_Y),
                                   counter))
        for command in commands:
            bus.bus.publish({'command': command}, bus.WORLD_EVENT)
        print(self.tavern.tavern_map.tiles[11][9].wall)

    def call_command(self, command):
        bus.bus.publish({'command': command}, bus.WORLD_EVENT)

    def add_object(self, obj, x, y):
        self.call_command(PutCommand(self._build_area(x, y), obj))

    def tick_for(self, l=1):
        for i in range(1, l + 1):
            self.tavern.tick()