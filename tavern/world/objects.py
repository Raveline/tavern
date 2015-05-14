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


class ObjectTemplate(object):
    """A template for an object in the tavern."""
    def __init__(self, name, function, price, character,
                 blocks=False, rules=None, after_put=None):
        """
        Name is self-explanatory.
        Function must be a constant in Functions, indicates what the object
        is used for.
        Price is the price to buy this object.
        Character is the way it is printed.
        Blocks indicates if this objects means a tile is non-walkable.
        Rules is a list, a set of rules to follow when trying to put this object
        some where.
        After_put is a function (or None) to call after putting the object.
        This function should ALWAYS take the object and the world_map as
        parameter. It is generally used to add constant tasks."""
        self.function = function
        self.price = price
        self.character = character
        self.name = name
        self.blocks = blocks
        if rules is None:
            rules = []
        self.rules = rules
        self.after_put = after_put

    def __repr__(self):
        return self.name


class TavernObject(object):
    """A real object, instantiated, with properties taken
    from the template."""
    def __init__(self, template):
        self.template = template
        self.blocks = self.template.blocks
        self.name = self.template.name
        self.character = self.template.character
        self.function = self.template.function


class Rule(object):
    def check(self, world, x, y):
        pass

    def get_error_message(self):
        return self.error_message


class RoomsRule(Rule):
    """This rule specify an object has to be put in some
    specific rooms."""
    def __init__(self, rooms):
        self.rooms = rooms

    def check(self, world_map, x, y):
        room_type = world_map.get_room_at(x, y)
        return room_type in self.rooms

    def get_error_message(self):
        return "Can only be put in certain rooms"


class NotWallRule(Rule):
    def check(self, world_map, x, y):
        tile = world_map.tiles[y][x]
        if tile.wall:
            self.error_message = 'Cannot put this object on a wall.'
            return False
        return True


class DefaultRule(Rule):
    """The default position rule, that makes sure
    the tile is built, that there is not already an object."""
    def check(self, world_map, x, y):
        tile = world_map.tiles[y][x]
        if tile.tile_object is not None:
            self.error_message = 'There is already an object here.'
            return False
        elif not tile.built:
            self.error_message = 'The are is not built.'
            return False
        return True


class OrRule(Rule):
    """A metarule, that says that one of two
    rules must be true."""
    def __init__(self, one, two):
        self.one = one
        self.two = two

    def check(self, world_map, x, y):
        return (self.one.check(world_map, x, y) or
                self.two.check(world_map, x, y))


class NextToWallRule(Rule):
    """Only valid is next to a wall."""
    def check(self, world_map, x, y):
        wall_neihgbours = [t for t in world_map.get_neighboring_for(x, y)
                           if t.wall]
        return len(wall_neihgbours) > 0


class ExteriorWallRule(Rule):
    """Only valid if the tile is a wall giving on the outside."""
    def check(self, world_map, x, y):
        return world_map.is_an_outside_wall(x, y)
