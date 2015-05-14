from collections import defaultdict

import libtcodpy as libtcod
from tavern.utils import bus
from tavern.utils.geom import manhattan
from tavern.world.objects import Functions, rooms_to_name
from tavern.world.store import StorageSystem
from tavern.people.employees import make_recruit_out_of


class Tavern(object):
    """The abstract entity of a tavern, meaning its physical
    manifestation (the TavernMap), its financial situation (cash),
    its storage situation (StorageSystem) the people inside (creatures).
    """
    def __init__(self, width, height, cash=1500, tiles=None):
        self.tavern_map = TavernMap(width, height, tiles)
        # Storage
        self.store = StorageSystem()
        # Money
        self.cash = cash
        # Creatures
        self.creatures = []

    def add_creature(self, creature):
        self.creatures.append(creature)

    def remove_creature(self, creature):
        self.creatures.remove(creature)

    def tick(self):
        for crea in self.creatures:
            crea.tick(self.tavern_map)

    def handle_customer_event(self, event_data):
        if event_data.get('customer'):
            self.creatures.append(event_data.get('customer'))
        elif event_data.get('recruit'):
            recruit = event_data.get('recruit')
            # First, we remove our recruit from the existing creature list...
            self.creatures.remove(recruit)
            # Then we rebuild it, anew !
            new_recruit = make_recruit_out_of(recruit)
            # ... and we add it back to the list of creatures !
            self.creatures.append(new_recruit)

    def receive(self, event):
        event_data = event.get('data')
        if event.get('type') == bus.CUSTOMER_EVENT:
            self.handle_customer_event(event_data)
        elif event.get('type') == bus.WORLD_EVENT:
            command = event_data.get('command')
            if command:
                command.execute(self)

    def creature_at(self, x, y, z):
        cre = [c for c in self.creatures
               if c.x == x and c.y == y and c.z == z]
        if cre:
            return cre[0]


class TavernMap():
    """The map of a tavern, describing where things are,
    its rooms, entry points, etc."""
    def __init__(self, width, height, cash=1000, tiles=None):
        # Dimensions
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
        # Pathfinding utility
        self.path_map = self._build_path_map()
        # A dict of all objects currently in use, by types
        self.used_objects_coords = defaultdict(list)
        # A dict of all objects currently being attended to by employees
        self.attended_objects_coords = defaultdict(list)
        # A dict of all objects attended to, but currently taken
        self.busy_attended_objects_coords = defaultdict(list)
        # Tasks requiring an employee
        # Those are accessible with Functions as key
        # The values is a ((x, y), task) tuple
        self.employee_tasks = defaultdict(list)
        # Seats (coords) that can be used
        self.available_seating = []
        # Seats (coords) that cannot be used because they are taken
        self.used_seating = []

    def can_serve_at(self, service, x, y):
        return (x, y) in self.attended_objects_coords.get(service)

    def take_busy_attended(self, function, x, y):
        self.attended_objects_coords.get(function).remove((x, y))
        self.busy_attended_objects_coords.get(function).append((x, y))

    def free_busy_attended(self, function, x, y):
        self.busy_attended_objects_coords.get(function).remove((x, y))
        self.attended_objects_coords.get(function).append((x, y))

    def get_room_at(self, x, y):
        for room_type, lists in self.rooms.iteritems():
            for one_list in lists:
                if (x, y) in one_list:
                    return room_type
        return None

    def take_seat(self, x, y):
        self.used_seating.append((x, y))
        self.available_seating.remove((x, y))

    def open_seat(self, x, y):
        if (x, y) in self.used_seating:
            self.used_seating.remove((x, y))
        self.available_seating.append((x, y))

    def _build_path_map(self):
        path_map = libtcod.map_new(self.width, self.height)
        for idy, line in enumerate(self.tiles):
            for idx, tile in enumerate(line):
                libtcod.map_set_properties(path_map, idx, idy, False,
                                           tile.is_walkable())
        return path_map

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

    def get_neighboring_coords_for(self, x, y):
        return [(x2, y2) for x2, y2
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

    def get_legit_moves_from(self, x, y, z):
        """
        Return the tiles one can move from x, y and z.
        """
        return [(x2, y2, z) for (x2, y2) in
                self.get_neighboring_coords_for(x, y)
                if self.tiles[y2][x2].is_walkable()]

    def get_neighboring_for(self, x, y):
        """
        Given a x, y coords get the 8 connected coords,
        orthogonally or diagonnally, unless they are
        outside the map.
        """
        return [self.tiles[y2][x2] for x2, y2
                in self.get_neighboring_coords_for(x, y)]

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

    def __repr__(self):
        return "Tavern map of size %d, %d" % (self.width, self.height)

    def path_from_to(self, x, y, x2, y2):
        path = libtcod.path_new_using_map(self.path_map)
        libtcod.path_compute(path, x, y, x2, y2)
        return path

    def __coords_to_distance(self, coords, x, y):
        """
        Given a list of coords, compute the distances to a set of (x, y)
        (using manhattan distance).
        """
        return [manhattan(x, y, xc, yc) for xc, yc in coords]

    def find_closest_in(self, coords, x, y):
        """
        Given a list of coords, find and return the one that is the closest
        to the set (x, y).
        """
        distances = self.__coords_to_distance(coords, x, y)
        closest = min(distances)
        return coords[distances.index(closest)]

    def find_closest_room(self, x, y, room_type):
        """Given x and y, find the closest room_type given
        from this set of coords. Return all coords of the closest
        room."""
        rooms = self.rooms.get(room_type)
        if not rooms:
            return
        elif len(rooms) > 1:
            best_case = min(self.__coords_to_distance(rooms[0], x, y))
            best_case_room = rooms[0]
            for r in rooms[1:]:
                case = min(self.__coords_to_distance(rooms[0], x, y))
                if case < best_case:
                    best_case = case
                    best_case_room = r
            return best_case_room
        else:
            return rooms[0]

    def find_closest_to_wall_neighbour(self, x, y):
        """Given a tile a coordinates x,y, find an empty neighbour
        that is the closest to a wall. Returns a set of coordinate.
        (This is used for pub counters)."""
        legit = [(xc, yc) for xc, yc
                 in self.get_immediate_neighboring_coords(x, y)
                 if self.tiles[yc][xc].is_walkable()]
        if not legit:
            return None
        potentials = {}
        for px, py in legit:
            dirx, diry = (px - x), (py - y)
            potentials[(px, py)] = self.distance_to_a_wall(px, py, dirx, diry)
        minimum = potentials.values()[0]
        result = potentials.keys()[0]
        for k, v in potentials.iteritems():
            if v < minimum:
                minimum = v
                result = k
        return result

    def distance_to_a_wall(self, x, y, dirx, diry):
        """Count the distance in tiles to a wall from the coords
        x, y going in the direction dirx, diry."""
        if self.tiles[y][x].wall or not self.tiles[y][x].built:
            return 0
        found_wall = False
        counter = 0
        while not found_wall:
            x += dirx
            y += diry
            if self.tiles[y][x].wall:
                return counter
            counter += 1

    def find_closest_object(self, x, y, function, to_attend=True):
        """Given an object type and a set of coords,
        search for the object of this type the closest to
        the set of coords. We will not return the coordinates
        of an object in use.
        To differentiate between USAGE by patron, and ATTENDING by
        employees, the last parameter gives a flag to identify
        if we're looking from the point of view of a patron or the
        point of view of an employee.
        Return the coords of this object."""
        if to_attend:
            unusable = self.attended_objects_coords[function]
            inlist = self.list_tiles_with_objects(function, unusable)
        else:
            inlist = self.attended_objects_coords[function]
        if inlist:
            return self.find_closest_in(inlist, x, y)

    def add_walkable_tile(self, x, y):
        libtcod.map_set_properties(self.path_map, x, y, False, True)

    def update_tile_walkability(self, x, y):
        libtcod.map_set_properties(self.path_map, x, y,
                                   False, self.tiles[y][x].is_walkable())

    def list_tiles_with_objects(self, function, exclusion_list=None):
        objects_coords = []
        for idy, line in enumerate(self.tiles):
            for idx, tile in enumerate(line):
                if tile.has_object_with_function(function):
                    if exclusion_list and (idx, idy) in exclusion_list:
                            continue
                    objects_coords.append((idx, idy))
        return objects_coords


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
