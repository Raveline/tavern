import libtcodpy as tcod
import groggy.events.bus as bus
from groggy.game.game import Game
from groggy.viewport.scape import Crosshair, Fillhair, Selection
from groggy.utils.tcod_wrapper import Console
from groggy.utils.geom import Frame
from tavern.view.show_console import display, print_selection, display_text
from tavern.view.show_console import display_creatures
from groggy.ui.component_builder import build_menu
from tavern.ui.informer import Informer
from tavern.ui.status import Status
from tavern.ui.state import MenuState, BuyMenuState, MenuState
from tavern.world.customers import Customers
from tavern.world.actions import door, counter, chair, oven, work_station
from tavern.world.map_commands import BuildCommand, PutCommand, RoomCommand
from tavern.world.world import Tavern
from tavern.world.actions import action_tree
from tavern.world import actions


MAP_WIDTH = 100
MAP_HEIGHT = 100

TITLE = 'The Tavern'


def main():
    game = TavernGame(TITLE, 80, 60)
    game.loop()


class TavernGame(Game):
    def test_bootstrap(self):
        def build_area(x, y, z=None, x2=None, y2=None):
            if z is None:
                z = 0
            if x2 is None:
                x2 = x
            if y2 is None:
                y2 = y
            area = Selection(x, y, z)
            area.x2 = x2
            area.y2 = y2
            return area
        # Build a storage area
        commands = []
        commands.append(BuildCommand(build_area(2, 2, 0, 5, 5)))
        # build a corridor to a tavern room
        commands.append(BuildCommand(build_area(5, 3, 0, 9, 4)))
        commands.append(PutCommand(build_area(8, 3, 0, 8, 4), door))
        # Build the tavern room
        commands.append(BuildCommand(build_area(9, 2, 0, 12, 12)))
        commands.append(PutCommand(build_area(11, 1), door))
        # Build the kitchen
        commands.append(BuildCommand(build_area(1, 7, 0, 7, 14)))
        commands.append(BuildCommand(build_area(8, 12)))
        commands.append(PutCommand(build_area(8, 12), door))
        for command in commands:
            bus.bus.publish({'command': command}, bus.WORLD_EVENT)
        commands = []
        commands.append(RoomCommand(self.tavern.tavern_map.fill_from((3, 3, 0)), 1))
        commands.append(RoomCommand(
            self.tavern.tavern_map.fill_from((10, 10, 0)), 0))
        commands.append(RoomCommand(
            self.tavern.tavern_map.fill_from((3, 10, 0)), 2))
        commands.append(PutCommand(build_area(9, 11), counter))
        commands.append(PutCommand(build_area(9, 6), chair))
        commands.append(PutCommand(build_area(5, 7, 0, 7, 9), oven))
        commands.append(PutCommand(build_area(4, 7), work_station))
        for command in commands:
            bus.bus.publish({'command': command}, bus.WORLD_EVENT)
        self.customers.tick_counter += 100

    def initialize_consoles(self):
        self.status_console = Console(0, 0, self.width, 1)
        self.world_console = Console(0, 1, self.width, self.height - 3)
        self.text_console = Console(0, self.height - 2, self.width, 2)

    def initialize_world(self):
        self.tavern = Tavern(MAP_WIDTH, MAP_HEIGHT)
        bus.bus.subscribe(self.tavern, bus.WORLD_EVENT)
        bus.bus.subscribe(self.tavern, bus.CUSTOMER_EVENT)
        self.customers = Customers(self.tavern)

        self.informer = Informer(self.text_console)
        bus.bus.subscribe(self.informer, bus.FEEDBACK_EVENT)

        self.status = Status(self.status_console)
        bus.bus.subscribe(self.status, bus.STATUS_EVENT)

        self.world_frame = Frame(0, 0, MAP_WIDTH, MAP_HEIGHT)
        self.cross = Crosshair(self.width, self.height, self.world_frame)
        self.filler = Fillhair(self.width, self.height, self.world_frame,
                               self.tavern.tavern_map.fill_from)

    def setup_first_state(self):
        self.change_state(GameState(action_tree, self.cross))
        bus.bus.subscribe(self, bus.GAME_EVENT)
        bus.bus.subscribe(self, bus.NEW_STATE)
        bus.bus.subscribe(self, bus.PREVIOUS_STATE)

        self.receiver = self.cross
        self.continue_game = True

    def display_background(self):
        display(self.clip_world(self.tavern.tavern_map.tiles[0],
                                self.receiver.scape.frame),
                self.world_console.console)

    def display_characters(self):
        display_list = [crea for crea in self.tavern.creatures
                        if self.receiver.scape.frame.contains(crea.x, crea.y)]
        display_creatures(self.world_console.console, display_list,
                          self.cross.global_to_local)

    def display_text(self):
        tcod.console_clear(self.text_console.console)
        self.informer.display()

    def display_navigation(self, blink):
        if self.state.navigator:
            if not blink:
                print_selection(self.world_console.console,
                                self.state.navigator)
            cre = self.get_selected_customer()
            if cre:
                self.describe_creature(cre)
            else:
                self.describe_area()

    def model_tick(self):
        self.tavern.tick()
        self.customers.tick()

    def display(self, blink):
        self.display_background()
        self.display_characters()
        self.display_status()
        self.display_text()
        self.display_navigation(blink)
        self.world_console.blit_on(0)
        self.text_console.blit_on(0)
        self.status_console.blit_on(0)
        self.state.display(0)

    def loop(self):
        self.test_bootstrap()
        super(TavernGame, self).loop()

    def display_status(self):
        self.status.pause = self.state.pauses_game
        self.status.money = self.tavern.cash
        self.status.current_state = str(self.state)
        self.status.display()

    def get_selected_customer(self):
        return self.tavern.creature_at(self.state.navigator.getX(),
                                       self.state.navigator.getY(),
                                       0)

    def __build_menu_state(self, tree):
        context = self.context.to_context_dict()
        clazz = MenuState
        data = self.tavern
        menu_type = tree.get('menu_type')
        if menu_type == 'BuyMenu':
            clazz = BuyMenuState
        elif menu_type == 'PricesMenu':
            clazz = PricesMenuState
        elif menu_type == 'Help':
            clazz = HelpMenuState
            data = self.state
            context['state'] = self.state.to_keys_array()
        elif menu_type == 'ExamineMenu':
            examined = self.get_selected_customer()
            if examined and examined.examinable:
                clazz = ExamineMenu
                data = examined
            else:
                return None
        root_component = build_menu(context, tree.get('content'), True)
        return clazz({}, root_component, self.state, data)

    def build_state(self, tree):
        if tree.get('type', '') == 'menu':
            return self.__build_menu_state(tree)
        elif tree.get('type', '') == 'box':
            return MenuState({}, tree.get('box'), self.state)
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
        self.state.activate()

    def describe_area(self):
        x, y = self.state.navigator.getX(), self.state.navigator.getY()
        pos = (x, y, self.state.navigator.getZ())
        tile = self.tavern.tavern_map[pos]
        text = "(%d, %d) - %s" % (x, y, tile.describe())
        display_text(self.text_console.console, text, 0, 0)

    def describe_creature(self, c):
        display_text(self.text_console.console, str(c), 0, 0)

    def receive(self, event):
        event_data = event.get('data')
        if event.get('type', '') == bus.NEW_STATE:
            new_state = self.build_state(event_data)
            if new_state is not None:
                self.change_state(new_state)
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
