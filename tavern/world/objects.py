class Functions:
    SITTING = 0,            # Object you can use to sit
    EATING = 1,             # Object you can eat / drink
    ROOM_SEPARATOR = 2,     # Commonly known as doors
    ORDERING = 3,           # Counter
    SUPPORT = 4             # Support for floors


class Rooms(object):
    TAVERN = 0
    STORAGE = 1
    KITCHEN = 2
    MEETING_ROOM = 3
    ROOM = 4


class Materials(object):
    WOOD = 0


rooms_to_name = {Rooms.TAVERN: 'Tavern',
                 Rooms.STORAGE: 'Storage',
                 Rooms.KITCHEN: 'Kitchen',
                 Rooms.MEETING_ROOM: 'Meeting room',
                 Rooms.ROOM: 'Room'}


class TavernObject(object):
    def __init__(self, name, function, price, character,
                 blocks=False, rules=None):
        self.function = function
        self.price = price
        self.character = character
        self.name = name
        self.blocks = blocks
        if rules is None:
            rules = []
        self.rules = rules

    def __repr__(self):
        return self.name


class Rule(object):
    def check(self, world, x, y):
        pass

    def get_error_message(self):
        return "You shouldn't see this"


class RoomsRule(object):
    """This rule specify an object has to be put in some
    specific rooms."""
    def __init__(self, rooms):
        self.rooms = rooms

    def check(self, world, x, y):
        room_type = world.get_room_at(x, y)
        return room_type in self.rooms

    def get_error_message(self):
        return "Can only be put in certain rooms"


class DefaultRule(object):
    """The default position rule, that makes sure
    the tile is built, that there is not already an object."""
    def check(self, world, x, y):
        tile = world.tavern_map.tiles[y][x]
        if tile.tile_object is not None:
            self.error_message = 'There is already an object here.'
            return False
        elif not tile.built:
            self.error_message = 'The are is not built.'
            return False
        return True

    def get_error_message(self):
        return self.error_message


class OrRule(object):
    """A metarule, that says that one of two
    rules must be true."""
    def __init__(self, one, two):
        self.one = one
        self.two = two

    def check(self, world, x, y):
        return self.one.check(world, x, y) or self.two.check(world, x, y)


class NextToWallRule(object):
    """Only valid is next to a wall."""
    def check(self, world, x, y):
        wall_neihgbours = [t for t in world.tavern_map.get_neighboring_for(x, y)
                           if t.wall]
        return len(wall_neihgbours) > 0


class ExteriorWallRule(object):
    """Only valid if the tile is a wall giving on the outside."""
    def check(self, world, x, y):
        return world.tavern_map.is_an_outside_wall(x, y)
