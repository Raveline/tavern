class Functions:
    SITTING = 0,            # Object you can use to sit
    EATING = 1,             # Object you can eat / drink
    ROOM_SEPARATOR = 2,     # Commonly known as doors
    ORDERING = 3,           # Counter
    SUPPORT = 4             # Support for floors


class Rooms(object):
    TAVERN = 0
    STORAGE = 1
    ROOM = 2


class TavernObject(object):
    def __init__(self, name, function, price, character):
        self.function = function
        self.price = price
        self.character = character
        self.name = name

    def __repr__(self):
        return self.name
