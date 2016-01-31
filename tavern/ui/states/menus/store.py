from groggy.ui.state import MenuState
from tavern.world.commands import BuyCommand
from groggy.utils.dict_path import read_path_dict


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
                'step': goods.get_quantity_for_a_cell(),
                'price': (str(goods.get_bulk_price()) +
                          " by " + str(goods.get_container())),
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
        self.set_data(self.build_data(self.world))
