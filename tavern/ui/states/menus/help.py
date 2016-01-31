from groggy.ui.state import MenuState


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
