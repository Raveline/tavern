import libtcodpy as libtcod
from tavern.utils.tcod_wrapper import Console


class RootComponent(object):
    """ A component with an attached console."""

    def __init__(self, x, y, w, h, title, children):
        self.console = Console(x, y, w, h)
        self.title = title
        self.children = children

    def deactivate(self):
        libtcod.console_delete(self.console)

    def display(self, console):
        """
        Display a frame, a title and children components.
        Then blit on the console parameter.
        """
        libtcod.console_print_frame(self.console.console,
                                    self.console.x + 1,
                                    self.console.y + 1,
                                    self.console.w - 1,
                                    self.console.h - 1, True)
        libtcod.console_print_ex(self.console.console, 0, self.console.w / 2,
                                 libtcod.BKGND_SET,
                                 libtcod.CENTER,
                                 self.title)
        for child in self.children:
            child.display(self.console.console)
        self.console.blit_on(console)


class Component(object):
    def __init__(self, x, y, w=0, h=0):
        self.x = x
        self.y = y
        self.w = 0
        self.h = 0
        pass


class TextBlocComponent(Component):
    def __init__(self, x, y, w, text):
        super(TextBlocComponent, self).__init__(x, y, w)
        self.text = text

    def display(self, console):
        libtcod.console_print_rect(console, self.x, self.y,
                                   self.w, 0, self.text)


def make_textbox(x, y, w, h, title, text):
    tbc = TextBlocComponent(1, 1, w - 1, text)
    root_component = RootComponent(x, y, w, h, title, [tbc])
    return root_component
