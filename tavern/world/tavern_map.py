from collections import defaultdict

import libtcodpy as tcod
from groggy.utils.geom import manhattan

from tavern.world.objects.functions import Functions
from tavern.world.objects.objects import rooms_to_name


class TavernMap():
    """The map of a tavern, describing where things are,
    its rooms, entry points, etc."""
    def __init__(self, width, height, cash=1000, tiles=None):
        # Dimensions
        self.width = width
        self.height = height
        # A map-imitating fbm
        self.background = self._build_background()
        # A 3D list of tiles
        self.tiles = tiles
        # The rooms defined by the player
        self.rooms = defaultdict(list)
        # Entry points to the tavern (main door)
        self.entry_points = []
        if not self.tiles:
            self.tiles = self._build_tiles()
        # Pathfinding utility
        self.path_map = self._build_path_map()
        # A dict of all objects currently in use, by types
        self.used_services = defaultdict(list)
        # A dict of all objects currently being attended to by employees
        self.available_services = defaultdict(list)

    def service_list(self, service):
        return self.available_services[service]

    def can_serve_at(self, service, pos):
        """Check if a service is available at position pos.

        param service: A constant from Functions
        type service: int

        param pos: A set of 3D coords
        type pos : A tuple (int, int, int)
        """
        return pos in self.available_services[service]

    def get_room_at(self, pos):
        """Get what type of room is at position pos.

        param pos: A set of 3D coords
        type pos: A tuple (int, int, int)
        """
        for room_type, lists in self.rooms.items():
            for one_list in lists:
                if pos in one_list:
                    return room_type
        return None

    def take_service(self, function, pos):
        """
        Make the service at position pos temporarily unavailable because
        a customer is using it.

        param function: A constant from the Functions list
        type function: int

        param pos: A set of 3D coords
        type pos: A tuple (int, int, int)
        """
        self.used_services[function].append(pos)
        try:
            self.available_services[function].remove(pos)
        except:
            print("There was no available service of type %d in %d, %d, %d"
                  % (function, pos[0], pos[1], pos[2]))
            exit(0)

    def open_service(self, function, pos):
        """
        Make a service available for all. It might be used :
            - When an employee is necessary for a service to be active and
            that the employee is now here.
            - When a service was being used by a customer, and that the
            customer is done.

        param function: A constant from the Functions list
        type function: int

        param pos: A set of 3D coords
        type pos: A tuple (int, int, int)
        """
        if pos in self.used_services[function]:
            self.used_services[function].remove(pos)
        self.available_services[function].append(pos)

    def stop_service(self, function, pos):
        """
        Remove a service from the available list. Used when a service is
        dependant on an employee and that this employee is not attending
        to the service anymore.

        param function: A constant from the Functions list
        type function: int

        param pos: A set of 3D coords
        type pos: A tuple (int, int, int)
        """
        self.available_services[function].remove(pos)

    def _build_path_map(self):
        path_map = []
        for idz, column in enumerate(self.tiles):
            floor_map = tcod.map_new(self.width, self.height)
            path_map.append(floor_map)
            for idy, line in enumerate(column):
                for idx, tile in enumerate(line):
                    tcod.map_set_properties(floor_map, idx, idy, False,
                                            tile.is_walkable())
        return path_map

    def _build_tiles(self):
        return [[[Tile(x, y, z, self.background[y][x])
                for x in range(self.width)]
                for y in range(self.height)]
                for z in range(10)]

    def fill_from(self, pos):
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
        x, y, z = pos
        tile = self.tiles[z][y][x]
        open_list = []
        if fillable(tile):
            open_list.append((x, y, z))
        while open_list:
            x_, y_, z_ = open_list.pop()
            fill_list.append((x_, y_, z_))
            tiles = self.get_immediate_neighboring_coords((x_, y_, z_))
            for tx, ty, tz in tiles:
                tile_ = self.tiles[tz][ty][tx]
                if fillable(tile_) and (tx, ty, tz) not in fill_list:
                    open_list.append((tx, ty, tz))
        return fill_list

    def _build_background(self):
        """
        Make a background noise that will more or less look like
        an old map.
        """
        noise = tcod.noise_new(2)
        tcod.noise_set_type(noise, tcod.NOISE_SIMPLEX)
        background = []
        for y in range(self.height):
            background.append([])
            for x in range(self.width):
                background[y].append(
                    tcod.noise_get_turbulence(noise,
                                              [y / 100.0, x / 100.0], 32.0))
        tcod.noise_delete(noise)
        return background

    def is_an_outside_wall(self, pos):
        """
        Make sure a tile is a wall and that this wall gives to the exterior.
        This means that the wall is next to a border, or connected to an
        unbuilt tile.
        (Note : this logic is flawed, since an enclosed unbuilt area
        is possible.)
        """
        neighbors = self.get_immediate_neighboring_coords(pos)
        if len(neighbors) < 4:
            return True
        for (nx, ny, nz) in neighbors:
            tile = self.tiles[nz][ny][nx]
            if not tile.built:
                return True
        return False

    def get_neighboring_coords_for(self, pos):
        x, y, z = pos
        return [(x2, y2, z2) for x2, y2, z2
                in [(x - 1, y - 1, z),
                    (x, y - 1, z),
                    (x + 1, y - 1, z),
                    (x - 1, y, z),
                    (x + 1, y, z),
                    (x - 1, y + 1, z),
                    (x, y + 1, z),
                    (x + 1, y + 1, z)]
                if x2 >= 0 and x2 < self.width and
                y2 >= 0 and y2 < self.height]

    def get_legit_moves_from(self, pos):
        """
        Return the tiles one can move from x, y and z.
        """
        return [(x, y, z) for (x, y, z) in
                self.get_neighboring_coords_for(pos)
                if self.tiles[z][y][x].is_walkable()]

    def get_neighboring_for(self, pos):
        """
        Given a x, y coords get the 8 connected coords,
        orthogonally or diagonnally, unless they are
        outside the map.
        """
        return [self.tiles[z][y][x] for x, y, z
                in self.get_neighboring_coords_for(pos)]

    def get_immediate_neighboring_coords(self, pos):
        """
        Given a tile coordinate, get all orthogonal
        neighbors coords of this tile if unless they
        are outside the map.
        """
        x, y, z = pos
        return [(x2, y2, z2) for x2, y2, z2
                in [(x, y - 1, z),
                    (x - 1, y, z),
                    (x + 1, y, z),
                    (x, y + 1, z)]
                if x2 >= 0 and x2 < self.width and
                y2 >= 0 and y2 < self.height]

    def __repr__(self):
        return "Tavern map of size %d, %d" % (self.width, self.height)

    def path_from_to(self, pos_origin, pos_destination):
        # For the moment, we do not handle Z movement
        x, y, z = pos_origin
        x2, y2, _ = pos_destination
        path = tcod.path_new_using_map(self.path_map[z])
        tcod.path_compute(path, x, y, x2, y2)
        return path

    def __coords_to_distance(self, coords, pos):
        """
        Given a list of coords, compute the distances to a set of (x, y)
        (using manhattan distance).
        """
        x, y, _ = pos
        return [manhattan(x, y, xc, yc) for xc, yc, __ in coords]

    def find_closest_in(self, coords, pos):
        """
        Given a list of coords, find and return the one that is the closest
        to the set (x, y).
        Or return None if coords is empty.
        """
        distances = self.__coords_to_distance(coords, pos)
        if distances:
            closest = min(distances)
            return coords[distances.index(closest)]

    def find_closest_room(self, pos, room_type):
        """Given x and y, find the closest room_type given
        from this set of coords. Return all coords of the closest
        room."""
        rooms = self.rooms.get(room_type)
        if not rooms:
            return
        elif len(rooms) > 1:
            best_case = min(self.__coords_to_distance(rooms[0], pos))
            best_case_room = rooms[0]
            for r in rooms[1:]:
                case = min(self.__coords_to_distance(rooms[0], pos))
                if case < best_case:
                    best_case = case
                    best_case_room = r
            return best_case_room
        else:
            return rooms[0]

    def find_closest_to_wall_neighbour(self, pos):
        """Given a tile a coordinates x,y, find an empty neighbour
        that is the closest to a wall. Returns a set of coordinate.
        (This is used for pub counters)."""
        x, y, z = pos
        legit = [pos2 for pos2
                 in self.get_immediate_neighboring_coords(pos)
                 if self[pos2].is_walkable()]
        if not legit:
            return None
        potentials = {}
        for px, py, pz in legit:
            dirx, diry = (px - x), (py - y)
            potentials[(px, py, z)] = self.distance_to_a_wall((px, py, pz),
                                                              (dirx, diry, pz))
        minimum = list(potentials.values())[0]
        result = list(potentials.keys())[0]
        for k, v in potentials.items():
            if v < minimum:
                minimum = v
                result = k
        return result

    def distance_to_a_wall(self, pos, dir_pos):
        """Count the distance in tiles to a wall from the coords
        x, y going in the direction dirx, diry."""
        x, y, z = pos
        dirx, diry, __ = dir_pos
        if self[pos].wall or not self[pos].built:
            return 0
        found_wall = False
        counter = 0
        while not found_wall:
            x += dirx
            y += diry
            if self.tiles[z][y][x].wall:
                return counter
            counter += 1

    def find_closest_object(self, pos, function):
        """Given an object type and a set of coords,
        search for the object of this type the closest to
        the set of coords. We will not return the coordinates
        of an object in use.
        To differentiate between USAGE by patron, and ATTENDING by
        employees, the last parameter gives a flag to identify
        if we're looking from the point of view of a patron or the
        point of view of an employee.
        Return the coords of this object."""
        return self.find_closest_in(self.available_services[function], pos)

    def add_walkable_tile(self, pos):
        x, y, z = pos
        tcod.map_set_properties(self.path_map[z], x, y, False, True)

    def update_tile_walkability(self, pos):
        x, y, z = pos
        tcod.map_set_properties(self.path_map[z], x, y, False,
                                self[pos].is_walkable())

    def list_tiles_with_objects(self, function, exclusion_list=None):
        objects_coords = []
        for idz, column in enumerate(self.tiles):
            for idy, line in enumerate(column):
                for idx, tile in enumerate(line):
                    if tile.has_object_with_function(function):
                        if exclusion_list and (idx, idy) in exclusion_list:
                            continue
                        objects_coords.append((idx, idy))
        return objects_coords

    def __getitem__(self, pos):
        x, y, z = pos
        return self.tiles[z][y][x]


class Tile(object):
    def __init__(self, x, y, z, background=0):
        self.x = x
        self.y = y
        self.z = z
        self.material = None
        self.wall = False
        self.built = False
        self.background = background
        self.tile_object = None
        self.room_type = None

    def is_walkable(self):
        return not self.wall and self.built and\
            (not self.tile_object or
             (self.tile_object and not self.tile_object.blocks))

    def has_object_with_function(self, function):
        return self.tile_object and self.tile_object.function == function

    def is_separating_tile(self):
        return self.has_object_with_function(Functions.ROOM_SEPARATOR)

    def describe(self):
        return ''.join([self.describe_nature(),
                       ' --- ',
                        self.describe_object()])

    def describe_nature(self):
        if self.wall:
            return "Wall"
        elif not self.built:
            return "Outside"
        elif self.room_type is not None:
            return rooms_to_name[self.room_type]
        else:
            return "Empty space"

    def describe_object(self):
        if self.tile_object:
            return self.tile_object.name
        else:
            return ''
