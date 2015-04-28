from tavern.utils import bus
from tavern.utils.callbackdict import CallbackDict
from tavern.inputs.input import Inputs
from tavern.world.goods import DRINKS
NEW_STATE = 0


class GameState(object):
    def __init__(self, state_tree, navigator=None, parent_state=None):
        self.tree = state_tree
        self.parent_state = parent_state
        self.navigator = navigator
        self.name = self.tree.get('name', '')
        self.action = self.tree.get('action', '')
        self.sub_object = None

    def deactivate(self):
        pass

    def activate(self):
        self.sub_object = None

    def receive(self, event):
        def pick_substate(event_data):
            substate = self.tree.get(event_data)
            if substate:
                bus.bus.publish(substate,
                                bus.NEW_STATE)
            return substate

        def pick_subobject(event_data):
            subobject = self.tree.get('submenu', {}).get(event_data)
            if subobject:
                self.sub_object = subobject.get('subobject')
                bus.bus.publish(str(self) + " : " + subobject.get('display'))
            return subobject

        event_data = event.get('data')
        if (event.get('type') == bus.INPUT_EVENT):
            if not (pick_substate(event_data) or
                    pick_subobject(event_data) or
                    self._check_for_previous_state(event_data))\
                    and self.navigator:
                self.navigator.receive(event_data)
        elif (event.get('type') == bus.AREA_SELECT):
            need_subobject = (bool(self.tree.get('submenu')) and
                              self.sub_object is None)
            if not need_subobject:
                bus.bus.publish({'area': event_data,
                                 'action': self.action,
                                 'complement': self.sub_object},
                                bus.WORLD_EVENT)
            elif need_subobject:
                keys = ['(' + k + ')' for k in self.tree.get('submenu').keys()]
                bus.bus.publish('Pick between ' + ', '.join(keys))

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
            return True
        return False

    def display(self, console):
        pass

    def __repr__(self):
        return self.name


class MenuState(GameState):
    def __init__(self, state_tree, root_component, parent_state=None,
                 data=None):
        super(MenuState, self).__init__(state_tree, None, parent_state)
        self.root_component = root_component
        self.set_data(data)

    def set_data(self, data):
        self.root_component.set_data(data)

    def _check_for_previous_state(self, event_data):
        if event_data == Inputs.ESCAPE:
            bus.bus.publish(self.parent_state, bus.PREVIOUS_STATE)
            return True
        return False

    def deactivate(self):
        self.root_component.deactivate()

    def receive(self, event):
        event_data = event.get('data')
        if not self._check_for_previous_state(event_data):
            self.root_component.receive(event_data)

    def display(self, console):
        self.root_component.display(console)


class StoreMenuState(MenuState):
    def __init__(self, state_tree, root_component,
                 parent_state=None, world=None):
        self.world = world
        self.initial_data = {}
        super(StoreMenuState, self).__init__(
            state_tree, root_component, parent_state, self.build_data()
        )

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
            affordable = cash / goods.buying_price
            data[goods.name] = {
                'minimum': self.initial_data.get('minimum', quantity),
                'current': quantity,
                'maximum': min(storable, affordable)}
        data['storage'] = str(available_room)
        data['cash'] = str(cash)
        if not self.initial_data:
            self.initial_data = data.copy()
        return CallbackDict(self.callback, data)

    def name_to_goods(self, key):
        goods = self.world.store.store.keys()
        with_name = [g for g in goods if g.name == key]
        return with_name[0]

    def callback(self, key, old_value, new_value):
        good = self.name_to_goods(key)
        # Cancelling sale
        if new_value < old_value:
            repayment = (old_value - new_value) * good.price
            self.world.cash += repayment
        # Buying
        elif new_value > old_value:
            payment = (new_value - old_value) * good.price
            self.world.cash -= payment
        self.set_data(self.build_data())
        return True
