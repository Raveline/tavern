from tavern.world.objects import Functions, TavernObject, Rooms

CROSSHAIR = 0
FILLER = 1


class Actions:
    BUILD = 0
    BUILD_COST = 10
    PUT = 1
    ROOMS = 2


door = TavernObject('Door',
                    Functions.ROOM_SEPARATOR,
                    15,
                    '=')

chair = TavernObject('Chair',
                     Functions.SITTING,
                     5,
                     'o')

table = TavernObject('Table',
                     Functions.EATING,
                     10,
                     '*',
                     True)

counter = TavernObject('Counter',
                       Functions.ORDERING,
                       30,
                       '+',
                       True)

beam = TavernObject('Beam',
                    Functions.SUPPORT,
                    10,
                    '^',
                    True)

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
                     {'type': 'StaticText',
                      'x': 1,
                      'y': 1,
                      'content': 'Cash :'},
                     {'type': 'DynamicText',
                      'x': 20,
                      'y': 1,
                      'source': 'cash'},
                     {'type': 'StaticText',
                      'x': 1,
                      'y': 2,
                      'content': 'Storage room :'},
                     {'type': 'DynamicText',
                      'x': 20,
                      'y': 2,
                      'source': 'storage'},
                     {'type': 'Line',
                      'x': 0,
                      'w': '100%',
                      'y': 3},
                     {'type': 'Foreach',
                      'source': 'goods.supplies',
                      'do': [{'type': 'StaticText',
                              'x': 5,
                              'eat_line': False},
                             {'type': 'DynamicText',
                              'x': 25,
                              'source_builder': 'current'},
                             {'type': 'Ruler',
                              'x': 5,
                              'w': '80%'}]
                      }]}

prices_menu = {'type': 'RootComponent',
               'template': 'centered 5',
               'title': 'Prices',
               'children': [
                   {'type': 'Line',
                    'x': 0,
                    'w': '100%',
                    'y': 3},
                   {'type': 'Foreach',
                    'source': 'goods.supplies',
                    'do': [{'type': 'StaticText',
                            'x': 5,
                            'eat_line': False},
                           {'type': 'NumberPicker',
                            'minimum': 1,
                            'maximum': 100,
                            'x': 25,
                            'w': '80%'}]
                    }]}
action_tree = {'name': 'Main mode',
               'pauses_game': False,
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
                     'menu_type': 'BuyMenu',
                     'content': supplies_menu},
               'r': {'type': 'menu',
                     'menu_type': 'PricesMenu',
                     'content': prices_menu}
               }
