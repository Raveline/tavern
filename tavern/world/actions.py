from tavern.world.objects import Functions, TavernObject, Rooms

CROSSHAIR = 0
FILLER = 1


class Actions:
    BUILD = 0
    PUT = 1
    ROOMS = 2


door = TavernObject('Door',
                    Functions.ROOM_SEPARATOR,
                    0,
                    '=')

chair = TavernObject('Chair',
                     Functions.SITTING,
                     0,
                     'o')

table = TavernObject('Table',
                     Functions.EATING,
                     0,
                     '*')

counter = TavernObject('Counter',
                       Functions.ORDERING,
                       0,
                       '+')

beam = TavernObject('Beam',
                    Functions.SUPPORT,
                    0,
                    '^')

objects_tree = {'d': door,
                'c': chair,
                't': table,
                'o': counter,
                'b': beam}

room_types = {'t': Rooms.TAVERN,
              's': Rooms.STORAGE,
              'r': Rooms.ROOM}

action_tree = {'name': 'Main mode',
               'b': {'action': Actions.BUILD,
                     'name': 'Building mode',
                     'selector': CROSSHAIR,
                     'submenu': {}},
               'p': {'action': Actions.PUT,
                     'name': 'Object mode',
                     'selector': CROSSHAIR,
                     'submenu': objects_tree},
               'r': {'action': Actions.ROOMS,
                     'name': 'Room mode',
                     'selector': FILLER,
                     'submenu': room_types}}
