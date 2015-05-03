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
        self.pause = False

    def receive(self, event):
        event_data = event.get('data')
        if event_data.get('status') == 'drinks':
            if event_data.get('flag') == True:
                self.remove_flag(StatusFlags.NO_BASICS_DRINKS)
            else:
                self.add_flag(StatusFlags.NO_BASICS_DRINKS)

    def add_flag(self, flag):
        if flag not in self.flags:
            self.flags.append(flag)

    def remove_flag(self, flag):
        if flag in self.flags:
            self.flags.remove(flag)

    def display(self):
        libtcod.console_clear(self.console.console)
        if self.pause:
            display_text(self.console.console, "*PAUSED*", 0, 0)
        display_text(self.console.console, str(libtcod.sys_get_fps()), 10, 0)
        display_text(self.console.console, self.current_state, 15, 0)
        display_text(self.console.console, ("Cash : %s" % self.money), 50, 0)
        for idx, f in enumerate(self.flags):
            display_highlighted_text(self.console.console, f,
                                     self.console.w - idx - 1, 0)

    def __repr__(self):
        return "Status bar"
