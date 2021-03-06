import groggy.events.bus as bus
from groggy.ui.selection import Selection
from tavern.world.actions import (
    door, counter, chair, oven, work_station, brewing_vat
)
from tavern.world.map_commands import BuildCommand, PutCommand, RoomCommand


def test_bootstrap(game):
    def build_area(x, y, z=None, x2=None, y2=None):
        if z is None:
            z = 0
        if x2 is None:
            x2 = x
        if y2 is None:
            y2 = y
        area = Selection(x, y, z)
        area.x2 = x2
        area.y2 = y2
        return area
    # Build a storage area
    game.tavern.cash = 6000
    commands = []
    commands.append(BuildCommand(build_area(2, 2, 0, 5, 5)))
    # build a corridor to a tavern room
    commands.append(BuildCommand(build_area(5, 3, 0, 9, 4)))
    commands.append(PutCommand(build_area(8, 3, 0, 8, 4), door))
    # Build the tavern room
    commands.append(BuildCommand(build_area(9, 2, 0, 12, 12)))
    commands.append(PutCommand(build_area(11, 1), door))
    # Build the kitchen
    commands.append(BuildCommand(build_area(1, 7, 0, 7, 14)))
    commands.append(BuildCommand(build_area(8, 12)))
    commands.append(PutCommand(build_area(8, 12), door))
    # Build the brewery
    commands.append(BuildCommand(build_area(1, 16, 0, 7, 23)))
    commands.append(BuildCommand(build_area(7, 15)))
    commands.append(PutCommand(build_area(7, 15), door))
    for command in commands:
        bus.bus.publish({'command': command}, bus.WORLD_EVENT)
    commands = []
    commands.append(RoomCommand(game.tavern.tavern_map.fill_from(
        (3, 3, 0)), 1))
    # Make tavern room
    commands.append(RoomCommand(
        game.tavern.tavern_map.fill_from((10, 10, 0)), 0))
    # Make kitchen room
    commands.append(RoomCommand(
        game.tavern.tavern_map.fill_from((3, 10, 0)), 2))
    # Make brewery room
    commands.append(RoomCommand(
        game.tavern.tavern_map.fill_from((2, 17, 0)), 5))
    commands.append(PutCommand(build_area(9, 11), counter))
    commands.append(PutCommand(build_area(9, 6), chair))
    commands.append(PutCommand(build_area(5, 7, 0, 7, 9), oven))
    commands.append(PutCommand(build_area(3, 17, 0, 5, 19), brewing_vat))
    commands.append(PutCommand(build_area(4, 7), work_station))
    for command in commands:
        bus.bus.publish({'command': command}, bus.WORLD_EVENT)
    game.customers.tick_counter += 100
