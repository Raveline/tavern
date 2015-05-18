from tavern.utils import bus
from tavern.utils.dict_path import read_path_dict
from tavern.ui.component_builder import make_questionbox
from tavern.inputs.input import Inputs
from tavern.world.actions import Actions
from tavern.world.commands import BuyCommand
from tavern.world.map_commands import BuildCommand, PutCommand, RoomCommand
from tavern.world.goods import DRINKS
NEW_STATE = 0


class GameState(object):
    def __init__(self, state_tree, navigator=None, parent_state=None):
        self.tree = state_tree
        self.parent_state = parent_state
        self.navigator = navigator
        self.name = self.tree.get('name', '')
        # The specific action in this menu
        self.action = self.tree.get('action', '')
        # The sub-modes one can enter from here
        self.actions = state_tree.get('actions')
        # The complement of any action
        self.sub_object = None
        # The way this complement should be displayed
        self.sub_object_display = None
        # By default, every state pauses game but the main one
        self.pauses_game = state_tree.get('pauses_game', True)

    def deactivate(self):
        pass

    def activate(self):
        self.sub_object = None

    def receive(self, event):
        def pick_substate(event_data):
            if self.actions:
                substate = self.actions.get(event_data)
                if substate:
                    bus.bus.publish(substate,
                                    bus.NEW_STATE)
                    self.navigator.set_char()
                return substate

        def pick_subobject(event_data):
            subobject = self.tree.get('submenu', {}).get(event_data)
            if subobject:
                self.sub_object = subobject.get('subobject')
                self.sub_object_display = subobject.get('display')
                if not isinstance(self.sub_object, int):
                    if self.sub_object.is_multi_tile:
                        self.navigator.set_multi_char(self.sub_object.character,
                                                      self.sub_object.width,
                                                      self.sub_object.height)
                    else:
                        self.navigator.set_char(self.sub_object.character)

            return subobject

        def check_pause(event_data):
            if event_data == Inputs.SPACE:
                self.pauses_game = not self.pauses_game

        event_data = event.get('data')
        if (event.get('type') == bus.INPUT_EVENT):
            if not (pick_substate(event_data) or
                    pick_subobject(event_data) or
                    check_pause(event_data) or
                    self._check_for_previous_state(event_data))\
                    and self.navigator:
                self.navigator.receive(event_data)
        elif (event.get('type') == bus.AREA_SELECT):
            need_subobject = (bool(self.tree.get('submenu')) and
                              self.sub_object is None)
            if not need_subobject:
                self.send_command(event_data)
            elif need_subobject:
                keys = ['(' + k + ')' for k in self.tree.get('submenu').keys()]
                bus.bus.publish('Pick between ' + ', '.join(keys))

    def send_command(self, area):
        if self.action == Actions.BUILD:
            command = BuildCommand(area)
        elif self.action == Actions.PUT:
            command = PutCommand(area, self.sub_object)
        elif self.action == Actions.ROOMS:
            command = RoomCommand(area, self.sub_object)
        if command is not None:
            bus.bus.publish({'command': command}, bus.WORLD_EVENT)

    def _check_for_previous_state(self, event_data):
        """
        Go to previous state if and only if :
            - The escape key has been hit
            - There is no current selection in the navigator
            - There is a parent state
        """
        if event_data == Inputs.ESCAPE and\
            not self.navigator.selection and\
                self.parent_state is not None:
            bus.bus.publish(self.parent_state, bus.PREVIOUS_STATE)
            self.navigator.set_char()
            return True
        return False

    def display(self, console):
        pass

    def __repr__(self):
        if self.sub_object_display:
            return "%s : %s" % (self.name, self.sub_object_display)
        else:
            return self.name

    def to_keys_array(self):
        """Used to feed the help menu."""
        to_return = []
        for k in self.actions.keys():
            to_return.append(k)
        for k in self.tree.get('submenu', {}).keys():
            to_return.append(k)
        return to_return

    def to_actions_dict(self):
        """Used to display the help menu.
        Should only be used on main menu."""
        to_return = {}
        for k, v in self.actions.iteritems():
            to_return[k] = {'key': k, 'name': v['name']}
        for v in self.tree.get('submenu', []):
            to_return[k] = {'key': k, 'name': v['display']}
        return to_return


class MenuState(GameState):
    def __init__(self, state_tree, root_component, parent_state=None,
                 data=None):
        super(MenuState, self).__init__(state_tree, None, parent_state)
        bus.bus.subscribe(self, bus.MENU_MODEL_EVENT)
        self.root_component = root_component
        self.set_data(data)

    def set_data(self, data):
        self.data = data
        self.root_component.set_data(data)

    def _check_for_previous_state(self, event_data):
        if event_data == Inputs.ESCAPE:
            bus.bus.publish(self.parent_state, bus.PREVIOUS_STATE)
            return True
        return False

    def deactivate(self):
        bus.bus.unsubscribe(self, bus.MENU_MODEL_EVENT)
        self.root_component.deactivate()

    def update_data_dict(self, source, new):
        data = self.data
        path = source.split('.')
        for s in path[:-1]:
            data = data.get(s)
        data[path[-1]] = new
        return data

    def update_data(self, source, new):
        data = self.update_data_dict(self, source, new)
        self.set_data(data)

    def receive(self, event):
        event_data = event.get('data')
        if event.get('type') == bus.MENU_MODEL_EVENT:
            self.receive_model_event(event_data)
        else:
            if not self._check_for_previous_state(event_data):
                self.root_component.receive(event_data)

    def display(self, console):
        self.root_component.display(console)

    def receive_model_event(self, event_data):
        pass

    def __str__(self):
        return "Menu"


class StoreMenuState(MenuState):
    def __init__(self, state_tree, root_component,
                 parent_state=None, world=None):
        self.world = world
        super(StoreMenuState, self).__init__(
            state_tree, root_component, parent_state, self.build_data()
        )

    def receive_model_event(self, event_data):
        self.update_data(event_data.get('source'),
                         event_data.get('new_value'))


class BuyMenuState(StoreMenuState):
    def __init__(self, state_tree, root_component,
                 parent_state=None, world=None):
        self.initial_data = {}
        super(BuyMenuState, self).__init__(state_tree, root_component,
                                           parent_state, world)

    def build_data(self):
        data = {}
        store = self.world.store
        cash = self.world.cash
        available_room = store.current_available_cells()
        # Currently, we will do this only for drinks, but chances are
        # this will need to be abstracted
        for goods in DRINKS:
            quantity = store.amount_of(goods)
            storable = store.cell_to_goods_quantity(available_room, goods)
            affordable = int(cash / goods.buying_price)
            minimum = self.initial_data.get(goods.name, {}).\
                get('minimum', quantity)
            data[goods.name] = {
                'obj': goods,
                'minimum': minimum,
                'current': quantity,
                'maximum': quantity + min(storable, affordable)}
        data['storage'] = str(available_room)
        data['cash'] = str(cash)
        if not self.initial_data:
            self.initial_data = data.copy()
        return data

    def update_data(self, source, new_value):
        goods = read_path_dict(self.data, source + ".obj")
        old_value = read_path_dict(self.data, source + ".current")
        quantity_diff = new_value - old_value
        if quantity_diff != 0:
            # Buying
            if quantity_diff > 0:
                command = BuyCommand(goods, quantity_diff)
            # Cancelling sale
            else:
                command = BuyCommand(goods, quantity_diff, True)
            command.execute(self.world)
            self.set_data(self.build_data())


class PricesMenuState(StoreMenuState):
    def build_data(self):
        data = {}
        for goods in DRINKS:
            data[goods.name] = {
                'obj': goods,
                'minimum': 0,
                'current': goods.selling_price,
                'maximum': 100
            }
        return data

    def update_data(self, source, new_value):
        goods = read_path_dict(self.data, source + ".obj")
        goods.selling_price = new_value
        self.set_data(self.build_data())


class HelpMenuState(MenuState):
    def __init__(self, state_tree, root_component,
                 parent_state=None, informed_state=None):
        self.informed_state = informed_state
        super(HelpMenuState, self).__init__(
            state_tree, root_component, parent_state, self.build_data()
        )

    def build_data(self):
        data = {}
        data = self.informed_state.to_actions_dict()
        return data


class ExamineMenu(MenuState):
    def __init__(self, state_tree, root_component,
                 parent_state=None, creature=None):
        self.creature = creature
        super(ExamineMenu, self).__init__(
            state_tree, root_component, parent_state, self.build_data())

    def receive_model_event(self, event_data):
        box = make_questionbox(5, 5, 60, 10,
                               'Recruit ?',
                               'Are you sure you want to recruit this '
                               'customer ?', self, [{'recruit': self.creature},
                                                    self.parent_state],
                               [bus.CUSTOMER_EVENT, bus.PREVIOUS_STATE])
        bus.bus.publish({'type': 'box', 'box': box}, bus.NEW_STATE)

    def build_data(self):
        data = {}
        data['name'] = 'PLACEHOLDER'
        data['level'] = str(self.creature.level)
        data['race'] = self.creature.race_string()
        data['class'] = self.creature.class_string()
        data['money'] = self.__money_to_string(self.creature.money)
        data['thirst'] = self.__desire_to_string(self.creature.thirst)
        data['activity'] = str(self.creature.current_activity)
        return data

    def __money_to_string(self, money):
        if money == 0:
            return "Pennyless"
        elif money <= 10:
            return "Broke"
        elif money <= 20:
            return "Has coins"
        elif money <= 30:
            return "Heavy purse"
        elif money <= 50:
            return "Wealthy"
        elif money <= 200:
            return "Rich"
        else:
            return "High roller"

    def __desire_to_string(self, desire):
        if desire == 0:
            return "None"
        elif desire == 1:
            return "Small"
        elif desire == 2:
            return "Medium"
        elif desire == 3:
            return "Severe"
        else:
            return "Enormous"
