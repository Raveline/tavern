from groggy.events import bus
from groggy.ui.state import MenuState
from tavern.world.goods import build_beer


class NewBrewMenu(MenuState):
    def __init__(self, state_tree, root_component, parent_state, goods):
        super(NewBrewMenu, self).__init__(
            state_tree, root_component, parent_state, self.build_data(goods)
        )
        self.goods = goods

    def build_data(self, goods):
        return {'grains': [{'object': g, 'selected': False}
                           for g in goods.grains],
                'aromas': [{'object': g, 'selected': False}
                           for g in goods.aromas],
                'roasted': False,
                'name': ''}

    def find_in_list_and_update(self, list_, element):
        row = next(r for r in list_ if r['object'] == element)
        row['selected'] = not row['selected']

    def update_data(self, source, new_value):
        if source not in ('grains', 'aromas'):
            self.source = self.data[source] = new_value
            self.set_data(self.data)

    def receive_model_event(self, event_data):
        if event_data.get('source'):
            self.update_data(event_data.get('source'),
                             event_data.get('new_value'))
        else:
            self.create_beer_and_leave(self.data)

    def create_beer_and_leave(self, data):
        grains = [g['object'] for g in self.data['grains'] if g['selected']]
        aromas = [a['object'] for a in self.data['aromas'] if a['selected']]
        if not grains:
            bus.bus.publish('Cannot make a beer without any grains')
            return
        beer, recipe = build_beer(grains, aromas, self.data['roasted'],
                                  self.data['name'])
        self.goods.add_drink(beer, recipe)
        self.call_previous_state()
