from tavern.utils import bus
from tavern.inputs.input import Inputs
NEW_STATE = 0


class GameState(object):
    def __init__(self, state_tree, navigator=None, parent_state=None):
        self.tree = state_tree
        self.parent_state = parent_state
        self.navigator = navigator
        self.name = self.tree.get('name', '')
        self.action = self.tree.get('action', '')
        self.sub_object = None

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
                self.sub_object = subobject
            return subobject

        def previous_state(event_data):
            if event_data == Inputs.ESCAPE and self.parent_state is not None:
                bus.bus.publish(self.parent_state,
                                bus.PREVIOUS_STATE)
                return True

        event_data = event.get('data')
        if (event.get('type') == bus.INPUT_EVENT):
            if not (pick_substate(event_data)
                    or pick_subobject(event_data)
                    or previous_state(event_data)) and self.navigator:
                self.navigator.receive(event_data)
        elif (event.get('type') == bus.AREA_SELECT):
            bus.bus.publish({'area': event_data,
                             'action': self.action,
                             'complement': self.sub_object},
                            bus.WORLD_EVENT)

    def __repr__(self):
        if self.sub_object:
            return "%s (%s)" % (self.name, self.sub_object)
        else:
            return self.name
