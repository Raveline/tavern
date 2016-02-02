from groggy.ui.state import MenuState
from tavern.world.objects.functions import Functions
from tavern.world.goods import GoodsType
from tavern.people.tasks.employee import FollowRecipe


class OrderMenu(MenuState):
    def __init__(self, state_tree, root_component, parent_state=None,
                 world=None):
        self.goods = world.goods
        self.world = world
        super(OrderMenu, self).__init__(state_tree, root_component,
                                        parent_state, self.build_data())

    def build_data(self):
        data = {}
        for good_type, dic in self.goods.recipes.items():
            for goods, recipe in dic.items():
                data[goods.name] = {
                    'obj': goods,
                    'step': goods.get_quantity_for_a_cell(),
                    'minimum': 0,
                    'current': 0,
                    'maximum': 100
                }
        return data

    def receive_model_event(self, event_data):
        if event_data.get('source'):
            source = event_data.get('source')
            self.data[source]['current'] = event_data.get('new_value')

    def deactivate(self):
        """
        On leaving, we need to make sure to call all necessary
        tasks.
        """
        super(OrderMenu, self).deactivate()
        for goods in self.data.values():
            if goods['current'] > 0:
                recipe = self.goods.recipes[GoodsType.CLASSIC_DRINKS][goods['obj']]
                batches = goods['current'] // goods['obj'].get_quantity_for_a_cell()
                for i in range(batches):
                    self.world.tasks.add_task(Functions.BREWING, None,
                                              FollowRecipe(recipe))
