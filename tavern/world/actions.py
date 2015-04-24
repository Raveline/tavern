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

objects_tree = {'d': {'display': 'Door', 'subobject': door},
                'c': {'display': 'Chair', 'subobject': chair},
                't': {'display': 'Table', 'subobject': table},
                'o': {'display': 'Counter', 'subobject': counter},
                'b': {'display': 'Beam', 'subobject': beam}}

room_types = {'t': {'display': 'Tavern', 'subobject': Rooms.TAVERN},
              's': {'display': 'Storage', 'subobject': Rooms.STORAGE},
              'r': {'display': 'Storage', 'subobject': Rooms.ROOM}}

supplies_menu = {'type': 'RootComponent',
                 'template': 'centered 5',
                 'title': 'Supplies',
                 'children': [
                     {'type': 'DynamicText',
                      'x': 5,
                      'y': 1,
                      'centered': True,
                      'source': 'test'}]
                 }

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
                     'submenu': room_types},
               's': {'type': 'menu',
                     'content': supplies_menu,
                     'data': {'test': 'This is a test display'}}
               }
