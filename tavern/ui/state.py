from groggy.events import bus
from groggy.utils.dict_path import read_path_dict
from groggy.ui.component_builder import make_choice_box
from groggy.inputs.input import Inputs
from groggy.ui.state import ScapeState, MenuState

from tavern.events.events import CUSTOMER_EVENT
from tavern.world.actions import Actions
from tavern.world.commands import BuyCommand
from tavern.world.map_commands import BuildCommand, PutCommand, RoomCommand
from tavern.people.employees import JOBS
NEW_STATE = 0


class TavernGameState(ScapeState):
    def __init__(self, state_tree, parent_state=None, scape=None):
        super(TavernGameState, self).__init__(state_tree, parent_state, scape)
        self.sub_object = None
        self.sub_object_display = None
        """This sub_object should also have a way to be displayed."""

    def activate(self):
        self.sub_object = None

    def pick_subobject(self, event_data):
        subobject = self.tree.get('submenu', {}).get(event_data)
        if subobject:
            self.sub_object = subobject.get('subobject')
            self.sub_object_display = subobject.get('display')
            self.change_sub_object_display()
        return subobject

    def check_pause(self, event_data):
        if event_data == Inputs.SPACE:
            self.pauses_game = not self.pauses_game

    def change_sub_object_display(self):
        if not isinstance(self.sub_object, int):
            if self.sub_object.is_multi_tile():
                self.scape.set_multi_char(self.sub_object.character,
                                          self.sub_object.width,
                                          self.sub_object.height)
            else:
                self.scape.set_char(self.sub_object.character)

    def dispatch_input_event(self, event_data):
        if not (self.pick_substate(event_data) or
                self.pick_subobject(event_data) or
                self.check_pause(event_data)):
            self.scape.receive(event_data)

    def send_command(self, area):
        command = None
        if self.action == Actions.BUILD:
            command = BuildCommand(area)
        elif self.action == Actions.PUT:
            command = PutCommand(area, self.sub_object)
            self.change_sub_object_display()
        elif self.action == Actions.ROOMS:
            command = RoomCommand(area, self.sub_object)
        if command:
            bus.bus.publish({'command': command}, bus.WORLD_EVENT)


class StoreMenuState(MenuState):
    def __init__(self, state_tree, root_component,
                 parent_state=None, world=None):
        self.world = world
        super(StoreMenuState, self).__init__(
            state_tree, root_component, parent_state, self.build_data(world)
        )

    def receive_model_event(self, event_data):
        self.update_data(event_data.get('source'),
                         event_data.get('new_value'))


class BuyMenuState(StoreMenuState):
    def __init__(self, state_tree, root_component,
                 parent_state=None, data=None):
        self.initial_data = {}
        super(BuyMenuState, self).__init__(state_tree, root_component,
                                           parent_state, data)

    def build_data(self, context):
        data = {}
        store = self.world.tavern.store
        cash = self.world.tavern.cash
        available_room = store.current_available_cells()
        # Currently, we will do this only for drinks, but chances are
        # this will need to be abstracted
        for goods in self.world.goods.supplies:
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
        data['storage'] = {
            'minimum': 0,
            'maximum': store.current_available_cells(),
            'current': store.current_occupied_cells()
        }
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
            self.set_data(self.build_data(self.world))


class PricesMenuState(StoreMenuState):
    def build_data(self, context):
        data = {}
        for goods in self.world.goods.sellables:
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
        events = []
        for profile in JOBS.values():
            events.append([{'recruit': self.creature,
                           'profile': profile},
                           self.parent_state])
        box = make_choice_box(
            5, 5, 60, 'Recruit ?',
            'What job would you give this person ?', self,
            JOBS.keys(), events, [CUSTOMER_EVENT, bus.PREVIOUS_STATE])
        bus.bus.publish({'type': 'box', 'box': box}, bus.NEW_STATE)

    def build_data(self):
        data = {}
        data['name'] = self.creature.name
        data['level'] = str(self.creature.level)
        data['race'] = self.creature.race_string()
        data['class'] = self.creature.class_string()
        data['money'] = self.__money_to_string(self.creature.money)
        data['thirst'] = self.__desire_to_string(self.creature.needs.thirst)
        data['hunger'] = self.__desire_to_string(self.creature.needs.hunger)
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
