import libtcodpy as libtcod
import tavern.utils.bus as bus
from tavern.inputs.input import Inputs
from tavern.receivers.navigators import Crosshair, Fillhair
from tavern.utils.tcod_wrapper import Console
from tavern.utils.geom import Frame
from tavern.view.show_console import display, print_selection, display_text
from tavern.ui.state import GameState, MenuState, StoreMenuState
from tavern.ui.component_builder import build_menu
from tavern.ui.informer import Informer
from tavern.world.context import Context
from tavern.world.world import WorldMap
from tavern.world.actions import action_tree
from tavern.world import actions


MAP_WIDTH = 200
MAP_HEIGHT = 200

TITLE = 'The Tavern'


def main():
    game = Game()
    game.loop()


class Game(object):
    def __init__(self):
        self.context = Context()
        width = self.context.width
        height = self.context.height
        libtcod.console_init_root(width, height, TITLE)
        self.world_console = Console(0, 0, width, height - 2)
        self.text_console = Console(0, height - 2, width, 2)
        self.inputs = Inputs(bus.bus)

        self.world_map = WorldMap(MAP_WIDTH, MAP_HEIGHT)
        bus.bus.subscribe(self.world_map, bus.WORLD_EVENT)

        self.informer = Informer(self.text_console)
        bus.bus.subscribe(self.informer, bus.FEEDBACK_EVENT)

        self.world_frame = Frame(0, 0, MAP_WIDTH, MAP_HEIGHT)
        self.cross = Crosshair(width, height, self.world_frame)
        self.filler = Fillhair(width, height, self.world_frame,
                               self.world_map.fill_from)
        self.state = None
        self.change_state(GameState(action_tree, self.cross))
        bus.bus.subscribe(self, bus.GAME_EVENT)
        bus.bus.subscribe(self, bus.NEW_STATE)
        bus.bus.subscribe(self, bus.PREVIOUS_STATE)

        self.receiver = self.cross
        self.continue_game = True

    def loop(self):
        libtcod.sys_set_fps(60)
        counter = 0
        blink = False
        while self.continue_game:
            counter += libtcod.sys_get_last_frame_length()
            if counter >= .2:
                blink = not blink
                counter = 0
            self.inputs.poll()
            display(self.clip_world(self.world_map.tiles,
                                    self.receiver.scape.frame),
                    self.world_console.console)
            libtcod.console_clear(self.text_console.console)
            self.informer.display()
            if self.state.navigator:
                if not blink:
                    print_selection(self.world_console.console,
                                    self.state.navigator)
                self.describe_area()
            self.world_console.blit_on(0)
            self.text_console.blit_on(0)
            self.state.display(0)
            libtcod.console_flush()

    def build_state(self, tree):
        if tree.get('type', '') == 'menu':
            context = self.context.to_context_dict()
            root_component = build_menu(context, tree.get('content'), True)
            clazz = MenuState
            data = tree.get('data')
            if tree.get('menu_type') == 'StoreMenu':
                clazz = StoreMenuState
                data = self.world_map
            return clazz({}, root_component, self.state, data)
        else:
            if tree.get('selector', actions.CROSSHAIR) == actions.CROSSHAIR:
                navigator = self.cross
            elif tree.get('selector', actions.FILLER) == actions.FILLER:
                navigator = self.filler
            navigator.set_coords(self.state.navigator)
            return GameState(tree, navigator, self.state)

    def change_state(self, new_state):
        if self.state is not None:
            # Remove the old state from input receiving
            bus.bus.unsubscribe(self.state, bus.INPUT_EVENT)
            bus.bus.unsubscribe(self.state, bus.AREA_SELECT)
            self.state.deactivate()
        self.state = new_state
        # Add the new state to input receiving
        bus.bus.subscribe(self.state, bus.INPUT_EVENT)
        bus.bus.subscribe(self.state, bus.AREA_SELECT)
        bus.bus.publish(str(self.state))
        self.state.activate()

    def describe_area(self):
        x, y = self.state.navigator.getX(), self.state.navigator.getY()
        tile = self.world_map.tiles[y][x]
        display_text(self.text_console.console, tile.describe(), 0, 0)

    def receive(self, event):
        event_data = event.get('data')
        if event.get('type', '') == bus.NEW_STATE:
            self.change_state(self.build_state(event_data))
        elif event.get('type', '') == bus.PREVIOUS_STATE:
            self.change_state(event_data)
        elif event_data == 'quit':
            self.continue_game = False

    def clip_world(self, tiles, clip_box):
        clipped_y = tiles[clip_box.y:clip_box.y + clip_box.h]
        clipped = [t[clip_box.x:clip_box.x + clip_box.w] for t in clipped_y]
        return clipped

    def __repr__(self):
        return "Main"

if __name__ == "__main__":
    main()
