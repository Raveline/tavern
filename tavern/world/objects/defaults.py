from tavern.world.objects.functions import Functions
from tavern.world.objects.objects import ObjectTemplate, Rooms
from tavern.world.objects.rules import (
    RoomsRule, OrRule, NextToWallRule, ExteriorWallRule, NotWallRule
)
from tavern.people.tasks import Serving


def add_counter_helping_task(world_map, x, y):
    x2, y2 = world_map.find_closest_to_wall_neighbour(x, y)
    world_map.employee_tasks[Functions.ORDERING].\
        append(((x2, y2), Serving(Functions.ORDERING)))


door = ObjectTemplate('Door',
                      Functions.ROOM_SEPARATOR,
                      15,
                      '=', False,
                      [OrRule(NextToWallRule(), ExteriorWallRule())])

chair = ObjectTemplate('Chair',
                       Functions.SITTING,
                       5,
                       'o', False,
                       [NotWallRule()])

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

beam = ObjectTemplate('Beam',
                      Functions.SUPPORT,
                      10,
                      '^',
                      True,
                      [NotWallRule()])
