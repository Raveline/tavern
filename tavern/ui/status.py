import libtcodpy as libtcod
from tavern.view.show_console import display_text, display_highlighted_text


class StatusFlags:
    NO_BASICS_DRINKS = 'D'
    NO_FANCY_DRINKS = 'Q'
    NO_SERVICE = 'S'


class Status(object):
    def __init__(self, console):
        self.current_state = ''
        self.money = 0
        self.flags = []
        self.console = console

    def receive(self, event):
        pass

    def display(self):
        libtcod.console_clear(self.console.console)
        display_text(self.console.console, self.current_state, 0, 0)
        display_text(self.console.console, ("Cash : %s" % self.money), 50, 0)
        for idx, f in enumerate(self.flags):
            display_highlighted_text(self.console.console, f, 60, 0)

    def __repr__(self):
        return "Status bar"
