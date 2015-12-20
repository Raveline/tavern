'''This module contains all building-related commands.'''

from tavern.utils import bus
from tavern.world.commands import Command
from tavern.world.objects.objects import Rooms, Materials, TavernObject
from tavern.world.objects.rules import DefaultRule
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
        z = rect.z
        for y in range(rect.y, rect.y2 + 1):
            for x in range(rect.x, rect.x2 + 1):
                if func((x, y, z), *args):
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
            world.add_creature(Publican(self.area.x, self.area.y, self.area.z))

    def build(self, pos, tavern_map):
        """
        Make tiles "built" and surround them by walls.
        """
        x, y, z = pos
        if x == 0 or y == 0 or x == tavern_map.width - 1 or\
                y == tavern_map.height - 1:
            bus.bus.publish('Cannot build border-map tiles.')
            return False
        tile = tavern_map[pos]
        tile.built = True
        tile.wall = False
        tile.material = Materials.WOOD
        tavern_map.add_walkable_tile(pos)
        self.set_neighboring_tiles_to_wall(pos, tavern_map)
        return True

    def set_neighboring_tiles_to_wall(self, pos, tavern_map):
        """
        For each tiles around a built tile, make sure
        those are wall if they are not built and not wall already.
        """
        for tile in tavern_map.get_neighboring_for(pos):
            if not tile.built:
                tile.built = True
                tile.wall = True


class PutCommand(MapCommand):
    def __init__(self, area, object_type):
        self.object_type = object_type
        self.area = area

    def execute(self, world):
        if self.object_type.is_multi_tile():
            self.put_multi_objects(world.tavern_map, self.object_type)
            counter = 1
        else:
            preview_cost = self.get_area_size(self.area) * self.object_type.price
            if world.cash < preview_cost:
                bus.bus.publish('Not enough money to do this !')
                return
            counter = self.apply_to_area(self.area, self.put_object,
                                         world.tavern_map, self.object_type)
        world.cash -= (counter * self.object_type.price)

    def put_multi_objects(self, world_map, object_type):
        rules = object_type.rules + [DefaultRule()]

        rect = self.area
        z = rect.z
        for y in range(rect.y, rect.y2 + 1):
            for x in range(rect.x, rect.x2 + 1):
                for rule in rules:
                    if not rule.check(world_map, (x, y, z)):
                        bus.bus.publish(rule.get_error_message())
                        return
        z = rect.z
        for y in range(rect.y, rect.y2 + 1):
            for x in range(rect.x, rect.x2 + 1):
                relativex = x - rect.x
                relativey = y - rect.y
                new_object = TavernObject(object_type)
                does_block = object_type.blocks[relativey][relativex]
                character = object_type.character[relativey][relativex]
                new_object.blocks = does_block
                new_object.character = character
                world_map.update_tile_walkability((x, y, z))
                tile = world_map.tiles[z][y][x]
                tile.tile_object = new_object
        after_put = object_type.after_put
        if after_put is not None:
            after_put(object_type, world_map, (rect.x, rect.y, z))
        return True

    def put_object(self, pos, world_map, object_type):
        tile = world_map[pos]
        for rule in object_type.rules + [DefaultRule()]:
            if not rule.check(world_map, pos):
                bus.bus.publish(rule.get_error_message())
                return
        # If we reached this point, object is valid
        tile.tile_object = TavernObject(object_type)
        world_map.update_tile_walkability(pos)
        after_put = object_type.after_put
        if after_put is not None:
            after_put(object_type, world_map, pos)
        return True


class RoomCommand(MapCommand):
    def __init__(self, area, room_type):
        self.area = area
        self.room_type = room_type

    def execute(self, world):
        for pos in self.area:
            tile = world.tavern_map[pos]
            tile.room_type = self.room_type

        world.tavern_map.rooms[self.room_type].append(self.area)
        if self.room_type == Rooms.STORAGE:
            world.store.add_cells(len(self.area))
