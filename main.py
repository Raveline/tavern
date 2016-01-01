'''
Entrance point for Tavern. Build the game (and defines the TavernGame class,
an extension of groggy's Game class).
This is still a dev / sandbox version, and is bloated with testing utilities,
unperfect process, etc.
'''
import groggy.events.bus as bus
from groggy.game.game import Game
from groggy.viewport.scape import Crosshair, Fillhair, Selection
from groggy.utils.tcod_wrapper import Console
from groggy.utils.geom import Frame
from groggy.ui.state import MenuState
from groggy.ui.component_builder import build_menu
from groggy.ui.informer import Informer

from tavern.view.displayer import (
    STATUS_CONSOLE, WORLD_CONSOLE, TEXT_CONSOLE, TavernDisplayer
)
from tavern.people.employees import JOBS
from tavern.events.events import CUSTOMER_EVENT, STATUS_EVENT
from tavern.world.goods import GoodsList
from tavern.ui.status import Status
from tavern.ui.state import (
    TavernGameState, BuyMenuState, HelpMenuState, PricesMenuState,
    ExamineMenu)
from tavern.world.customers import Customers
from tavern.world.actions import door, counter, chair, oven, work_station
from tavern.world.map_commands import BuildCommand, PutCommand, RoomCommand
from tavern.world.tavern import Tavern
from tavern.world.world import World
from tavern.world.actions import action_tree
from tavern.world import actions


MAP_WIDTH = 100
MAP_HEIGHT = 100

TITLE = b'The Tavern'


def main():
    bus.bus.activate_debug_mode(True, [bus.INPUT_EVENT])
    game = TavernGame(TITLE, 80, 60)
    game.start_loop()


class TavernGame(Game):
    """
    Main engine, makes everything run.
    """

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
        commands.append(RoomCommand(self.tavern.tavern_map.fill_from(
            (3, 3, 0)), 1))
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
        return {
            STATUS_CONSOLE: Console(0, 0, self.width, 1),
            WORLD_CONSOLE: Console(0, 1, self.width, self.height - 3),
            TEXT_CONSOLE: Console(0, self.height - 2, self.width, 2)
        }

    def initialize_displayer(self):
        return TavernDisplayer(self.tavern, self.informer, self.status)

    def initialize_world(self):
        self.tavern = Tavern(MAP_WIDTH, MAP_HEIGHT)
        self.world = World(self.tavern, GoodsList(), JOBS)
        bus.bus.subscribe(self.world, bus.WORLD_EVENT)
        bus.bus.subscribe(self.world, CUSTOMER_EVENT)
        self.customers = Customers(self.tavern)

        self.informer = Informer()
        bus.bus.subscribe(self.informer, bus.FEEDBACK_EVENT)

        self.status = Status()
        bus.bus.subscribe(self.status, STATUS_EVENT)

        self.world_frame = Frame(0, 0, MAP_WIDTH, MAP_HEIGHT)
        self.cross = Crosshair(self.width, self.height, self.world_frame)
        self.filler = Fillhair(self.width, self.height, self.world_frame,
                               self.tavern.tavern_map.fill_from)

    def setup_first_state(self):
        self.change_state(TavernGameState(action_tree, scape=self.cross))

        self.receiver = self.cross
        self.continue_game = True

    def model_tick(self):
        self.world.tick()
        self.customers.tick()
        self.update_status()

    def before_loop(self):
        self.test_bootstrap()

    def loop_content(self, tick, blink):
        self.update_status()
        super(TavernGame, self).loop_content(tick, blink)

    def update_status(self):
        self.status.pause = self.state.pauses_game
        self.status.money = self.tavern.cash
        self.status.current_state = str(self.state)

    def __build_menu_state(self, tree):
        context = {'width': self.width,
                   'height': self.height}
        clazz = MenuState
        data = self.world
        menu_type = tree.get('menu_type')
        if menu_type == 'BuyMenu':
            clazz = BuyMenuState
            context['goods'] = {'supplies': self.world.goods.supplies}
        elif menu_type == 'PricesMenu':
            clazz = PricesMenuState
            context['goods'] = {'supplies': self.world.goods.sellables}
        elif menu_type == 'Help':
            clazz = HelpMenuState
            data = self.state
            context['state'] = self.state.to_keys_array()
        elif menu_type == 'TaskMenu':
            clazz = MenuState
            context['tasks'] = self.tavern.tasks.current_task_list()
        elif menu_type == 'ExamineMenu':
            examined = self.displayer.get_selected_customer(self.state)
            if examined and examined.examinable:
                clazz = ExamineMenu
                data = examined
            else:
                return None
        root_component = build_menu(context, tree.get('content'), True)
        return clazz({'name': 'Menu'}, root_component, self.state, data)

    def build_state(self, tree):
        tree_type = tree.get('type', '')
        if tree_type == 'menu':
            return self.__build_menu_state(tree)
        elif tree_type == 'box':
            return MenuState({'name': 'Box'}, tree.get('box'), self.state)
        else:
            if tree.get('selector', actions.CROSSHAIR) == actions.CROSSHAIR:
                navigator = self.cross
            elif tree.get('selector', actions.FILLER) == actions.FILLER:
                navigator = self.filler
            navigator.set_coords(self.state.scape)
            return TavernGameState(tree, self.state, navigator)

    def __repr__(self):
        return "Main"

if __name__ == "__main__":
    main()
