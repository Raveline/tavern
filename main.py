'''
Entrance point for Tavern. Build the game (and defines the TavernGame class,
an extension of groggy's Game class).
This is still a dev / sandbox version, and is bloated with testing utilities,
unperfect process, etc.
'''
from itertools import chain


import libtcodpy as tcod

import groggy.events.bus as bus
from groggy.game.game import Game
from groggy.viewport.scape import Viewport
from groggy.ui.selection import Crosshair, Fillhair
from groggy.utils.tcod_wrapper import Console
from groggy.utils.geom import Frame
from groggy.ui.state import MenuState
from groggy.ui.component_builder import build_menu
from groggy.ui.informer import Informer

from tavern.view.displayer import (
    STATUS_CONSOLE, WORLD_CONSOLE, TEXT_CONSOLE, TavernDisplayer
)
from tavern.people.employees import JOBS
from tavern.events.events import CUSTOMER_EVENT, STATUS_EVENT, MONEY_EVENT
from tavern.world.goods import GoodsList
from tavern.ui.status import Status
from tavern.ui.states.game import TavernGameState
from tavern.ui.states.menus import (
    BuyMenuState, HelpMenuState, PricesMenuState,
    ExamineMenu, NewBrewMenu, OrderMenu)
from tavern.world.customers import Customers
from tavern.world.tavern import Tavern
from tavern.world.world import World
from tavern.world.actions import action_tree
from tavern.world import actions


MAP_WIDTH = 100
MAP_HEIGHT = 100

TITLE = b'The Tavern'


def main():
    bus.bus.activate_debug_mode(True, [bus.INPUT_EVENT])
    tcod.console_set_custom_font(b'terminal.png',
                                 tcod.FONT_LAYOUT_ASCII_INROW)
    game = TavernGame(TITLE, 80, 60)
    game.start_loop()


class TavernGame(Game):
    """
    Main engine, makes everything run.
    """
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
        bus.bus.subscribe(self.status, MONEY_EVENT)

        self.world_frame = Frame(0, 0, MAP_WIDTH, MAP_HEIGHT)
        self.viewport = Viewport(self.width, self.height, self.world_frame)
        self.cross = Crosshair()
        self.filler = Fillhair(self.tavern.tavern_map.fill_from)

    def setup_first_state(self):
        self.change_state(TavernGameState(action_tree, viewport=self.viewport,
                                          selection=self.cross))

        self.receiver = self.cross
        self.continue_game = True

    def model_tick(self):
        self.world.tick()
        self.customers.tick()
        self.update_status()

    def before_loop(self):
        from tavern.debug import test_bootstrap
        test_bootstrap(self)

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
        elif menu_type == 'OrderMenu':
            clazz = OrderMenu
            data = self.world
            context['recipes'] = {
                'drinks': chain(*self.world.goods.recipes.values())
            }
        elif menu_type == 'TaskMenu':
            clazz = MenuState
            data = self.tavern.tasks.current_task_list()
            context['tasks'] = data
        elif menu_type == 'NewBrewMenu':
            clazz = NewBrewMenu
            data = self.goods
            context['grains'] = self.world.goods.grains
            context['aromas'] = self.world.goods.aromas
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
            navigator.set_coords(self.state.selection)
            return TavernGameState(tree, self.state, self.viewport, navigator)

    def __repr__(self):
        return "Main"

if __name__ == "__main__":
    main()
