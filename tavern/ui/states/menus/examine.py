from groggy.events import bus
from groggy.ui.component_builder import make_choice_box
from groggy.ui.state import MenuState

from tavern.events.events import CUSTOMER_EVENT
from tavern.people.employees import JOBS
NEW_STATE = 0


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
        data['sleep'] = self.__desire_to_string(self.creature.needs.sleep)
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
