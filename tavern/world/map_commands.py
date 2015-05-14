'''This module contains all building-related commands.'''

from tavern.utils import bus
from commands import Command
from tavern.world.objects import (
    Functions, Rooms, Materials, DefaultRule, TavernObject)
from tavern.people.employees import Publican


class MapCommand(Command):
    """As in "a command that applies to a tavern map"."""
    def apply_to_area(self, rect, func, *args):
        """
        Apply the function func (with args if any) to every
        tiles in the rect. Func should return a bool so that
        we can count the successful operation.
        """
        # Count the number of successful call to func
        count = 0
        for y in range(rect.y, rect.y2 + 1):
            for x in range(rect.x, rect.x2 + 1):
                if func(x, y, *args):
                    count += 1
        return count

    def get_area_size(self, rect):
        return (rect.y2 - rect.y) * (rect.x2 - rect.x)


class BuildCommand(MapCommand):
    COST = 10

    def __init__(self, area):
        self.area = area

    def execute(self, world):
        previewed_cost = self.get_area_size(self.area) * BuildCommand.COST
        if world.cash < previewed_cost:
            bus.bus.publish('Not enough money to do this !')
            return
        real_cost = self.apply_to_area(self.area, self.build,
                                       world.tavern_map) * BuildCommand.COST
        world.cash -= real_cost
        # If this is the first build, add a Publican
        if not world.creatures:
            world.add_creature(Publican(self.area.x, self.area.y))

    def build(self, x, y, tavern_map):
        """
        Make tiles "built" and surround them by walls.
        """
        if x == 0 or y == 0 or x == tavern_map.width - 1 or\
                y == tavern_map.height - 1:
            bus.bus.publish('Cannot build border-map tiles.')
            return False
        tile = tavern_map.tiles[y][x]
        tile.built = True
        tile.wall = False
        tile.material = Materials.WOOD
        tavern_map.add_walkable_tile(x, y)
        self.set_neighboring_tiles_to_wall(x, y, tavern_map)
        return True

    def set_neighboring_tiles_to_wall(self, x, y, tavern_map):
        """
        For each tiles around a built tile, make sure
        those are wall if they are not built and not wall already.
        """
        for tile in tavern_map.get_neighboring_for(x, y):
            if not tile.built:
                tile.built = True
                tile.wall = True


class PutCommand(MapCommand):
    def __init__(self, area, object_type):
        self.object_type = object_type
        self.area = area

    def execute(self, world):
        preview_cost = self.get_area_size(self.area) * self.object_type.price
        if world.cash < preview_cost:
            bus.bus.publish('Not enough money to do this !')
            return
        counter = self.apply_to_area(self.area, self.put_object,
                                     world.tavern_map, self.object_type)
        world.cash -= (counter * self.object_type.price)

    def put_object(self, x, y, world_map, object_type):
        tile = world_map.tiles[y][x]
        is_door = object_type.function == Functions.ROOM_SEPARATOR
        is_chair = object_type.function == Functions.SITTING
        is_destination_wall = tile.wall
        for rule in object_type.rules + [DefaultRule()]:
            if not rule.check(world_map, x, y):
                bus.bus.publish(rule.get_error_message())
                return
        # If we reached this point, object is valid
        # Special case for outside door
        if is_door and is_destination_wall:
            world_map.tiles[y][x].wall = False
            world_map.tiles[y][x].built = True
            world_map.entry_points.append((x, y))
            world_map.add_walkable_tile(x, y)
        else:
            tile.tile_object = TavernObject(object_type)
            if is_chair:
                print("Opening a chair...")
                world_map.open_seat(x, y)
            world_map.update_tile_walkability(x, y)
        return True


class RoomCommand(MapCommand):
    def __init__(self, area, room_type):
        self.area = area
        self.room_type = room_type

    def execute(self, world):
        for (x, y) in self.area:
            tile = world.tavern_map.tiles[y][x]
            tile.room_type = self.room_type

        world.tavern_map.rooms[self.room_type].append(self.area)
        if self.room_type == Rooms.STORAGE:
            world.store.add_cells(len(self.area))
