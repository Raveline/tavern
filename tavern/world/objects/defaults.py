from tavern.world.objects.functions import Functions
from tavern.world.objects.objects import ObjectTemplate
from tavern.world.objects.objects import Rooms
from tavern.world.objects.rules import (
    RoomsRule, OrRule, NextToWallRule, ExteriorWallRule, NotWallRule
)
from tavern.people.tasks.employee import Serving
import tavern.world.colors as Colors


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

door = ObjectTemplate(name='Door', function=Functions.ROOM_SEPARATOR, price=15,
                      character='=', color=Colors.DOOR_MAHOGANY, blocks=False,
                      rules=[OrRule(NextToWallRule(), ExteriorWallRule())],
                      after_put=add_entry_point)

chair = ObjectTemplate(name='Chair', function=Functions.SITTING, price=5,
                       character='o', color=Colors.CHAIR_WALNUT_STAIN,
                       blocks=False, rules=[NotWallRule()],
                       after_put=open_service)

table = ObjectTemplate(name='Table', function=Functions.EATING, price=10,
                       character='*', color=Colors.TABLE_BROWN, blocks=True,
                       rules=[RoomsRule([Rooms.TAVERN]), NotWallRule()])

counter = ObjectTemplate(name='Counter', function=Functions.ORDERING, price=30,
                         character='+', blocks=True,
                         color=Colors.COUNTER_LIGHT_WOOD,
                         rules=[RoomsRule([Rooms.TAVERN]), NotWallRule()],
                         after_put=add_counter_helping_task)

oven = ObjectTemplate(
    name='Oven', function=Functions.COOKING, price=100,
    character=['~~~', '~^~', '~ ~'],
    color=[[Colors.OVEN_BRICK, Colors.OVEN_BRICK, Colors.OVEN_BRICK],
           [Colors.OVEN_BRICK, Colors.FLAME_RED, Colors.OVEN_BRICK],
           [Colors.OVEN_BRICK, Colors.OVEN_BRICK, Colors.OVEN_BRICK]],
    blocks=[[True, True, True], [True, True, True], [True, False, True]],
    rules=[RoomsRule([Rooms.KITCHEN]), NotWallRule()], after_put=open_service,
    service_coords=[(1, 2)])

brewing_vat = ObjectTemplate(
    name='Brewing vat', function=Functions.BREWING, price=2000,
    character=['/-\\', '|o|', '\+/'],
    color=[[Colors.VAT_COPPER, Colors.VAT_COPPER, Colors.VAT_COPPER],
           [Colors.VAT_COPPER, Colors.VAT_COPPER, Colors.VAT_COPPER],
           [Colors.VAT_COPPER, Colors.VAT_COPPER, Colors.VAT_COPPER]],
    blocks=[[True, True, True], [True, True, True], [True, False, True]],
    rules=[RoomsRule([Rooms.BREWERY]), NotWallRule()], after_put=open_service,
    service_coords=[(1, 2)])

work_station = ObjectTemplate(
    name='Work station', function=Functions.WORKSHOP, price=20, character='=',
    color=Colors.WORKSHOP_ALBASTER, blocks=True,
    rules=[RoomsRule([Rooms.KITCHEN]), NotWallRule()], after_put=open_service)

beam = ObjectTemplate(name='Beam', function=Functions.SUPPORT, price=10,
                      character='^', color=Colors.BEAM_LIGHT_WOOD,
                      blocks=True, rules=[NotWallRule()])
