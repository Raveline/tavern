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
def add_counter_helping_task(object_type, world, pos):
    p = world.tavern_map.find_closest_to_wall_neighbour(pos)
    world.tasks.add_task(Functions.ORDERING, p,
                         Serving(Functions.ORDERING, p, True))


def add_entry_point(object_type, world, pos):
    world_map = world.tavern_map
    tile = world_map[pos]
    if tile.wall:
        tile.wall = False
        tile.built = True
        world_map.entry_points.append(pos)
        world_map.add_walkable_tile(pos)


def open_service(object_type, world, pos):
    world_map = world.tavern_map
    x, y, z = pos
    if object_type.is_multi_tile():
        for pos_x, pos_y in object_type.service_coords:
            x2, y2 = x + pos_x, y + pos_y
            if world_map.tiles[z][y2][x2].is_walkable():
                world_map.open_service(object_type.function, (x2, y2, z))
    else:
        if object_type.blocks:
            # The object blocks : the service is on all neighbouring tiles
            for (pos2) in world_map.get_immediate_neighboring_coords(pos):
                if world_map[pos2].is_walkable():
                    world_map.open_service(object_type.function, pos2)
        else:
            # The object does not block : the service is on the tile itself
            world_map.open_service(object_type.function, pos)

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
                      [(1, 2)])


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
