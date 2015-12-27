from groggy.events import bus
from tavern.world.objects.defaults import (door, chair, table,
                                           counter, beam, oven,
                                           work_station)
from tavern.world.objects.objects import Rooms

CROSSHAIR = 0
FILLER = 1


class Actions:
    BUILD = 0
    BUILD_COST = 10
    PUT = 1
    ROOMS = 2

objects_tree = {'d': {'display': 'Door', 'subobject': door},
                'c': {'display': 'Chair', 'subobject': chair},
                't': {'display': 'Table', 'subobject': table},
                'o': {'display': 'Counter', 'subobject': counter},
                'b': {'display': 'Beam', 'subobject': beam},
                'v': {'display': 'Oven', 'subobject': oven},
                'w': {'display': 'Workstation', 'subobject': work_station}}


room_types = {'t': {'display': 'Tavern', 'subobject': Rooms.TAVERN},
              's': {'display': 'Storage', 'subobject': Rooms.STORAGE},
              'r': {'display': 'Inn room', 'subobject': Rooms.ROOM},
              'k': {'display': 'Kitchen', 'subobject': Rooms.KITCHEN}}

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
                     {'type': 'Ruler',
                      'x': 20,
                      'y': 2,
                      'source': 'storage',
                      'selectable': False
                      },
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
                             {'type': 'NumberPicker',
                              'minimum': 1,
                              'maximum': 100,
                              'x': 5,
                              'w': '80%'}]
                      }]}

help_menu = {'type': 'RootComponent',
             'template': 'centered 5',
             'title': 'Help',
             'children': [{'type': 'Foreach',
                           'source': 'state',
                           'do': [{'type': 'DynamicText',
                                   'x': 5,
                                   'source_builder': 'key',
                                   'eat_line': False},
                                  {'type': 'DynamicText',
                                   'x': 20,
                                   'source_builder': 'name'}]
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

examine_menu = {'type': 'RootComponent',
                'template': 'centered 5',
                'title': 'Examine',
                'children': [
                    {'type': 'DynamicText',
                     'x': 5,
                     'y': 2,
                     'source': 'name'},
                    {'type': 'DynamicText',
                     'x': 25,
                     'y': 2,
                     'source': 'level'},
                    {'type': 'DynamicText',
                     'x': 35,
                     'y': 2,
                     'source': 'race'},
                    {'type': 'DynamicText',
                     'x': 50,
                     'y': 2,
                     'source': 'class'},
                    {'type': 'Line',
                     'x': 0,
                     'w': '100%',
                     'y': 3},
                    {'type': 'StaticText',
                     'x': 5,
                     'y': 5,
                     'content': 'Money'},
                    {'type': 'DynamicText',
                     'x': 25,
                     'y': 5,
                     'source': 'money'},
                    {'type': 'StaticText',
                     'x': 5,
                     'y': 6,
                     'content': 'Thirst'},
                    {'type': 'DynamicText',
                     'x': 25,
                     'y': 6,
                     'source': 'thirst'},
                    {'type': 'StaticText',
                     'x': 5,
                     'y': 7,
                     'content': 'Hunger'},
                    {'type': 'DynamicText',
                     'x': 25,
                     'y': 7,
                     'source': 'hunger'},
                    {'type': 'StaticText',
                     'x': 5,
                     'y': 9,
                     'content': 'Current activity'},
                    {'type': 'DynamicText',
                     'x': 25,
                     'y': 9,
                     'source': 'activity'},
                    {'type': 'Button',
                     'x': 25,
                     'y': 10,
                     'text': 'Recruit',
                     'event': 'recruit',
                     'event_type': bus.MENU_MODEL_EVENT}]}

task_menu= {'type': 'RootComponent',
            'template': 'centered 5',
            'title': 'Tasks',
            'children': [
                {'type': 'Line',
                 'x': 0,
                 'w': '100%',
                 'y': 3},
                {'type': 'Foreach',
                 'source': 'tasks',
                 'do': [{'type': 'StaticText',
                         'x': 5}]
                 }
            ]
            }

action_tree = {'name': 'Main mode',
               'pauses_game': False,
               'actions': {
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
                         'name': 'Buy supplies',
                         'menu_type': 'BuyMenu',
                         'content': supplies_menu},
                   'i': {'type': 'menu',
                         'name': 'Fix prices',
                         'menu_type': 'PricesMenu',
                         'content': prices_menu},
                   't': {'type': 'menu',
                         'name': 'Task menu',
                         'menu_type': 'TaskMenu',
                         'content': task_menu},
                   'e': {'type': 'menu',
                         'name': 'Examine',
                         'menu_type': 'ExamineMenu',
                         'content': examine_menu},
                   '?': {'type': 'menu',
                         'name': 'Get help',
                         'menu_type': 'Help',
                         'content': help_menu}
               }}
