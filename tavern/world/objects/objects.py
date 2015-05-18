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
        if isinstance(self.character, list):
            self.height = len(self.character)
            self.width = len(self.character[0][0])
        else:
            self.height = 1
            self.width = 1

    def __repr__(self):
        return self.name

    def is_multi_tile(self):
        return self.height > 1 or self.width > 1


class TavernObject(object):
    """A real object, instantiated, with properties taken
    from the template."""
    def __init__(self, template):
        self.template = template
        self.blocks = self.template.blocks
        self.name = self.template.name
        self.character = self.template.character
        self.function = self.template.function
