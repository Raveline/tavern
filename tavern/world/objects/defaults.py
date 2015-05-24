from tavern.world.objects.functions import Functions
from tavern.world.objects.objects import ObjectTemplate
from tavern.world.objects.objects import Rooms
from tavern.world.objects.rules import (
    RoomsRule, OrRule, NextToWallRule, ExteriorWallRule, NotWallRule
)
from tavern.people.tasks.tasks_employees import Serving


###
# After_put function should be stored here.
# This is a collection of utilities function
# with code that should be executed once you've
# put an object in the tavern.
# This callback pattern seems awful to me,
# and I'd much prefer a better way of doing this.
# TOPONDER : Find a better way of doing this.
###
def add_counter_helping_task(object_type, world_map, x, y):
    x2, y2 = world_map.find_closest_to_wall_neighbour(x, y)
    world_map.add_task(Functions.ORDERING, (x2, y2),
                       Serving(Functions.ORDERING, x2, y2, True))


def add_entry_point(object_type, world_map, x, y):
    tile = world_map.tiles[y][x]
    if tile.wall:
        tile.wall = False
        tile.built = True
        world_map.entry_points.append((x, y))
        world_map.add_walkable_tile(x, y)


def open_service(object_type, world_map, x, y):
    if object_type.is_multi_tile():
        for pos_x, pos_y in object_type.service_coords:
            x2, y2 = x + pos_x, y + pos_y
            if world_map.tiles[y2][x2].is_walkable():
                world_map.open_service(object_type.function, x2, y2)
    else:
        if object_type.blocks:
            # The object blocks : the service is on all neighbouring tiles
            for (x2, y2) in world_map.get_immediate_neighboring_coords(x, y):
                if world_map.tiles[y2][x2].is_walkable():
                    world_map.open_service(object_type.function, x2, y2)
        else:
            # The object does not block : the service is on the tile itself
            world_map.open_service(object_type.function, x, y)

door = ObjectTemplate('Door',
                      Functions.ROOM_SEPARATOR,
                      15,
                      '=', False,
                      [OrRule(NextToWallRule(), ExteriorWallRule())],
                      add_entry_point)

chair = ObjectTemplate('Chair',
                       Functions.SITTING,
                       5,
                       'o', False,
                       [NotWallRule()],
                       open_service)

table = ObjectTemplate('Table',
                       Functions.EATING,
                       10,
                       '*',
                       True,
                       [RoomsRule([Rooms.TAVERN]), NotWallRule()])

counter = ObjectTemplate('Counter',
                         Functions.ORDERING,
                         30,
                         '+',
                         True,
                         [RoomsRule([Rooms.TAVERN]), NotWallRule()],
                         add_counter_helping_task)

oven = ObjectTemplate('Oven',
                      Functions.COOKING,
                      100,
                      ['~~~',
                       '~^~',
                       '~ ~'],
                      [[True, True, True],
                       [True, True, True],
                       [True, False, True]],
                      [RoomsRule([Rooms.KITCHEN]), NotWallRule()],
                      open_service,
                      [(2, 1)])


work_station = ObjectTemplate('Work station',
                              Functions.WORKSHOP,
                              20,
                              '=',
                              True,
                              [RoomsRule([Rooms.KITCHEN]), NotWallRule()],
                              open_service)


beam = ObjectTemplate('Beam',
                      Functions.SUPPORT,
                      10,
                      '^',
                      True,
                      [NotWallRule()])
