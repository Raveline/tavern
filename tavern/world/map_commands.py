'''This module contains all building-related commands.'''

from tavern.utils import bus
from commands import Command
from tavern.world.objects import Functions, Rooms, Materials
from tavern.people.characters import Publican


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
        # TODO : add material
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
        self.apply_to_area(self.area, self.put_object,
                           world.tavern_map, self.object_type)

    def put_object(self, x, y, world_map, object_type):
        def validate_object_location(tile, object_type):
            if tile.tile_object is None and tile.built:
                if object_type.function == Functions.ROOM_SEPARATOR:
                    if world_map.tiles[y][x].wall:
                        # Wall. Door is only allowed if on exterior wall
                        if world_map.is_an_outside_wall(x, y):
                            world_map.tiles[y][x].wall = False
                            world_map.tiles[y][x].built = True
                            world_map.entry_points.append((x, y))
                            return True
                        else:
                            bus.bus.publish('Door to the outside must be on an'
                                            ' exterior wall.')
                            return False
                    if len([t for t in world_map.get_neighboring_for(x, y)
                            if t.wall]) > 0:
                        return True
                    else:
                        bus.bus.publish('Door must be next to a wall, or in'
                                        ' an exterior wall.')
                else:
                    return not tile.wall
            elif tile.tile_object is not None:
                bus.bus.publish('There is already an object here.')
            elif not tile.built:
                bus.bus.publish('The area is not built.')
            return False
        tile = world_map.tiles[y][x]
        if object_type and validate_object_location(tile, object_type):
            tile.tile_object = object_type
            if object_type.function == Functions.SITTING:
                world_map.open_seat(x, y)


class RoomCommand(MapCommand):
    def __init__(self, area, room_type):
        self.area = area
        self.room_type = room_type

    def execute(self, world):
        if self.room_type == Rooms.STORAGE:
            world.store.add_cells(len(self.area))
