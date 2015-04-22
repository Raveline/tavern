from collections import defaultdict

import libtcodpy as libtcod
from tavern.utils import bus
from tavern.world.actions import Actions
from tavern.world.objects import Functions, Rooms, rooms_to_name

WOOD = 'wood'


class WorldMap():
    def __init__(self, width, height, tiles=None):
        self.width = width
        self.height = height
        # A map-imitating fbm
        self.background = self._build_background()
        # A 2D (soon to be 3D !) list of tiles
        self.tiles = tiles
        # The rooms defined by the player
        self.rooms = defaultdict(list)
        # Entry points to the tavern (main door)
        self.entry_points = []
        if not self.tiles:
            self.tiles = self._build_tiles()

    def __repr__(self):
        return "World of size %d, %d" % (self.width, self.height)

    def receive(self, event):
        event_data = event.get('data', {})
        area = event_data.get('area')
        action = event_data.get('action')
        if action == Actions.BUILD:
            self.apply_to_area(area, self.build)
        elif action == Actions.PUT:
            self.apply_to_area(area, self.add_object,
                               event_data.get('complement'))
        elif action == Actions.ROOMS:
            self.add_room(area, event_data.get('complement'))

    def add_room(self, tiles, room_type):
        for (x, y) in tiles:
            tile = self.tiles[y][x]
            tile.room = room_type
        self.rooms[room_type].append(tiles)

    def add_object(self, y, x, object_type):
        def validate_object_location(tile, object_type):
            if tile.tile_object is None and tile.built:
                if object_type.function == Functions.ROOM_SEPARATOR:
                    if self.tiles[y][x].wall:
                        # Wall. Door is only allowed if on exterior wall
                        if self.is_an_outside_wall(x, y):
                            self.entry_points.append((x, y))
                            return True
                        else:
                            bus.bus.publish('Door to the outside must be on an'
                                            ' exterior wall.')
                            return False
                    if len([t for t in self.get_neighboring_for(x, y)
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

        tile = self.tiles[y][x]
        if object_type and validate_object_location(tile, object_type):
            tile.tile_object = object_type

    def _build_tiles(self):
        return [[Tile(x, y, self.background[y][x])
                for x in range(self.width)]
                for y in range(self.height)]

    def fill_from(self, x, y):
        """
        Filler function, mostly used to handle room definition.
        Will give all tiles from a starting coord that make an
        architectural unit - stopping at walls and doors.
        """
        def fillable(tile):
            return not tile.wall and\
                tile.built and\
                not tile.is_separating_tile()
        fill_list = []
        tile = self.tiles[y][x]
        open_list = []
        if fillable(tile):
            open_list.append((x, y))
        while open_list:
            x_, y_ = open_list.pop()
            fill_list.append((x_, y_))
            tiles = self.get_immediate_neighboring_coords(x_, y_)
            for t in tiles:
                tile_ = self.tiles[t[1]][t[0]]
                if fillable(tile_) and (t[0], t[1]) not in fill_list:
                    open_list.append((t[0], t[1]))
        return fill_list

    def _build_background(self):
        """
        Make a background noise that will more or less look like
        an old map.
        """
        noise = libtcod.noise_new(2)
        libtcod.noise_set_type(noise, libtcod.NOISE_SIMPLEX)
        background = []
        for y in range(self.width):
            background.append([])
            for x in range(self.height):
                background[y].append(
                    libtcod.noise_get_turbulence(noise,
                                                 [y / 100.0, x / 100.0],
                                                 32.0))
        libtcod.noise_delete(noise)
        return background

    def apply_to_area(self, rect, func, *args):
        """
        Apply the function func (with args if any) to every
        tiles in the rect.
        """
        for y in range(rect.y, rect.y2 + 1):
            for x in range(rect.x, rect.x2 + 1):
                func(y, x, *args)

    def build(self, y, x):
        """
        Make tiles "built" and surround them by walls.
        """
        if x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1:
            bus.bus.publish('Cannot build border-map tiles.')
            return
        tile = self.tiles[y][x]
        tile.built = True
        tile.wall = False
        tile.material = WOOD
        self.set_neighboring_tiles_to_wall(x, y)

    def set_neighboring_tiles_to_wall(self, x, y):
        """
        For each tiles around a built tile, make sure
        those are wall if they are not built and not wall already.
        """
        for tile in self.get_neighboring_for(x, y):
            if not tile.built:
                tile.built = True
                tile.wall = True

    def is_an_outside_wall(self, x, y):
        """
        Make sure a tile is a wall and that this wall gives to the exterior.
        This means that the wall is next to a border, or connected to an
        unbuilt tile.
        (Note : this logic is flawed, since an enclosed unbuilt area
        is possible.)
        """
        neighbors = self.get_immediate_neighboring_coords(x, y)
        if len(neighbors) < 4:
            return True
        for (nx, ny) in neighbors:
            tile = self.tiles[ny][nx]
            if not tile.built:
                return True
        return False

    def get_neighboring_for(self, x, y):
        """
        Given a x, y coords get the 8 connected coords,
        orthogonally or diagonnally, unless they are
        outside the map.
        """
        return [self.tiles[y2][x2] for x2, y2
                in [(x - 1, y - 1),
                    (x, y - 1),
                    (x + 1, y - 1),
                    (x - 1, y),
                    (x + 1, y),
                    (x - 1, y + 1),
                    (x, y + 1),
                    (x + 1, y + 1)]
                if x2 >= 0 and x2 < self.width and
                y2 >= 0 and y2 < self.height]

    def get_immediate_neighboring_coords(self, x, y):
        """
        Given a tile coordinate, get all orthogonal
        neighbors coords of this tile if unless they
        are outside the map.
        """
        return [(x2, y2) for x2, y2
                in [(x, y - 1),
                    (x - 1, y),
                    (x + 1, y),
                    (x, y + 1)]
                if x2 >= 0 and x2 < self.width and
                y2 >= 0 and y2 < self.height]


class Tile(object):
    def __init__(self, x, y, background=0):
        self.x = x
        self.y = y
        self.material = None
        self.wall = False
        self.built = False
        self.background = background
        self.tile_object = None
        self.room_type = None

    def is_separating_tile(self):
        return self.tile_object and\
            self.tile_object.function == Functions.ROOM_SEPARATOR

    def describe(self):
        return ''.join([self.describe_nature(),
                       ' --- ',
                       self.describe_object()])

    def describe_nature(self):
        if self.wall:
            return "Wall"
        elif not self.built:
            return "Outside"
        elif self.room_type:
            return rooms_to_name(self.room_type)
        else:
            return "Empty space"

    def describe_object(self):
        if self.tile_object:
            return self.tile_object.name
        else:
            return ''
