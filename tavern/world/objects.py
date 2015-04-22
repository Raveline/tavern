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


rooms_to_name = {Rooms.TAVERN: 'Tavern',
                 Rooms.STORAGE: 'Storage',
                 Rooms.KITCHEN: 'Kitchen',
                 Rooms.MEETING_ROOM: 'Meeting room',
                 Rooms.ROOM: 'Room'}


class TavernObject(object):
    def __init__(self, name, function, price, character):
        self.function = function
        self.price = price
        self.character = character
        self.name = name

    def __repr__(self):
        return self.name
