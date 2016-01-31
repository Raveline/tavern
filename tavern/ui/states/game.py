from groggy.events import bus
from groggy.inputs.input import Inputs
from groggy.ui.state import ViewportState
from tavern.world.actions import Actions
from tavern.world.map_commands import BuildCommand, PutCommand, RoomCommand


class TavernGameState(ViewportState):
    def __init__(self, state_tree, parent_state=None,
                 viewport=None, selection=None):
        super(TavernGameState, self).__init__(state_tree, parent_state,
                                              viewport, selection)
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
                self.selection.set_multi_char(self.sub_object.character,
                                              self.sub_object.width,
                                              self.sub_object.height)
            else:
                self.selection.set_char(self.sub_object.character)

    def dispatch_input_event(self, event_data):
        if not (self.pick_substate(event_data) or
                self.pick_subobject(event_data) or
                self.check_pause(event_data)):
            self.handle_selection_move(event_data)

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
