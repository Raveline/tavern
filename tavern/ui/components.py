import libtcodpy as libtcod
from tavern.utils.tcod_wrapper import Console, display_highlighted_text
from tavern.utils.tcod_wrapper import display_text


class Component(object):
    def __init__(self, x, y, w=0, h=0, is_selectable=False, children=None):
        self.x = x
        self.y = y
        self.w = 0
        self.h = 0
        self.is_selectable = is_selectable
        self.focused = False
        if children is None:
            children = []
        self.children = children


class RootComponent(Component):
    """ A component with an attached console."""
    def __init__(self, x, y, w, h, title, children):
        super(RootComponent, self).__init__(x, y, w, h, False, children)
        self.console = Console(x, y, w, h)
        self.title = title

    def deactivate(self):
        libtcod.console_delete(self.console)

    def display(self, console):
        """
        Display a frame, a title and children components.
        Then blit on the console parameter.
        """
        libtcod.console_set_default_foreground(self.console.console,
                                               libtcod.white)
        libtcod.console_hline(self.console.console, 0, 0, self.console.w)
        libtcod.console_hline(self.console.console, 0,
                              self.console.h - 1, self.console.w)
        libtcod.console_vline(self.console.console, 0, 0, self.console.h)
        libtcod.console_vline(self.console.console, self.console.w - 1,
                              0, self.console.h)
        libtcod.console_print_ex(self.console.console, self.console.w / 2, 0,
                                 libtcod.BKGND_SET,
                                 libtcod.CENTER,
                                 self.title)
        for child in self.children:
            child.display(self.console.console)
        self.console.blit_on(console)


class TextBlocComponent(Component):
    def __init__(self, x, y, w, text):
        super(TextBlocComponent, self).__init__(x, y, w)
        self.text = text

    def display(self, console):
        libtcod.console_print_rect(console, self.x, self.y,
                                   self.w, 0, self.text)


class RowsComponent(Component):
    def __init__(self, x, y, w=0, h=0, is_selectable=False, contents=None):
        super(RowsComponent).__init__(x, y, w, h, is_selectable)
        if contents is None:
            contents = []
        self.contents = contents
        self.compute_widths()

    def compute_widths(self):
        lens = [(len(col) for col in row) for row in self.contents]
        self.widths = [max(sizes) for sizes in lens]

    def display(self, console):
        libtcod.console_print


class ColumnedLine(Component):
    def __init__(self, x, y, is_selectable=False, widths=None, contents=None):
        if widths is None:
            widths = []
        if contents is None:
            contents = []
        super(ColumnedLine, super).__init__(x, y, sum(widths), 1, is_selectable)

    def display(self, console):
        current_x = self.x
        func = display_text
        if self.focus:
            func = display_highlighted_text
        for idx, elem in enumerate(self.contents):
            func(console, elem, current_x, self.y)
            current_x += self.widths[idx]


def make_textbox(x, y, w, h, title, text):
    tbc = TextBlocComponent(1, 1, w - 1, text)
    root_component = RootComponent(x, y, w, h, title, [tbc])
    return root_component
