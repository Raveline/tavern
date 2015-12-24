import libtcodpy as tcod
from groggy.view.displayer import Displayer
from tavern.view.show_console import display, print_selection, display_text
from tavern.view.show_console import display_creatures
from tavern.view.show_console import display_text, display_highlighted_text


STATUS_CONSOLE = 1
WORLD_CONSOLE = 2
TEXT_CONSOLE = 3


class TavernDisplayer(Displayer):
    def __init__(self, tavern, informer, status):
        super(TavernDisplayer, self).__init__(tavern)
        self.tavern = tavern
        self.informer = informer
        self.status = status

    def call(self, blink, state, consoles):
        world_console = consoles[WORLD_CONSOLE]
        if state.is_scape_state():
            self.display_background(state, world_console)
            self.display_characters(state, world_console)
            if not blink:
                print_selection(world_console.console, state.scape)
            cre = self.get_selected_customer(state)
            text_console = consoles[TEXT_CONSOLE]
            if cre:
                self.describe_creature(cre, text_console)
            else:
                self.describe_area(state, text_console)
        else:
            # Menu display
            state.root_component.display(world_console)

    def get_selected_customer(self, state):
        return self.tavern.creature_at(state.scape.getX(),
                                       state.scape.getY(),
                                       0)

    def display_background(self, state, console):
        display(self.clip_world(self.tavern.tavern_map.tiles[0],
                                state.scape.frame),
                console.console)

    def display_characters(self, state, console):
        display_list = [crea for crea in self.tavern.creatures
                        if state.scape.frame.contains(crea.x, crea.y)]
        display_creatures(console.console, display_list,
                          state.scape.global_to_local)

    def display_status(self, status, console):
        tcod.console_clear(console.console)
        if self.pause:
            display_text(console.console, "*PAUSED*", 0, 0)
        display_text(console.console, str(tcod.sys_get_fps()), 10, 0)
        display_text(console.console, status.current_state, 15, 0)
        display_text(console.console, ("Cash : %s" % self.money), 50, 0)
        for idx, f in enumerate(self.flags):
            display_highlighted_text(console.console, f,
                                     console.w - idx - 1, 0)

    def display_informer(self, console):
        tcod.console_clear(console.console)
        display_text(console.console, self.informer.text, 0, 1)
        self.informer.display()

    def describe_creature(self, creature, console):
        display_text(console.console, str(creature), 0, 0)

    def describe_area(self, state, console):
        x, y = state.scape.getX(), state.scape.getY()
        pos = (x, y, state.scape.getZ())
        tile = self.tavern.tavern_map[pos]
        text = "(%d, %d) - %s" % (x, y, tile.describe())
        display_text(console.console, text, 0, 0)
