from tavern.world.objects import Functions, TavernObject


class Actions:
    BUILD = 0
    PUT = 1


door = TavernObject(Functions.ROOM_SEPARATOR,
                    0,
                    '=')

chair = TavernObject(Functions.SITTING,
                     0,
                     'o')

table = TavernObject(Functions.EATING,
                     0,
                     '*')

counter = TavernObject(Functions.ORDERING,
                       0,
                       '+')

beam = TavernObject(Functions.SUPPORT,
                    0,
                    '^')

objects_tree = {'d': door,
                'c': chair,
                't': table,
                'o': counter,
                'b': beam}


action_tree = {'name': 'Main mode',
               'b': {'action': Actions.BUILD,
                     'name': 'Building mode',
                     'submenu': {}},
               'p': {'action': Actions.PUT,
                     'name': 'Object mode',
                     'submenu': objects_tree}}
