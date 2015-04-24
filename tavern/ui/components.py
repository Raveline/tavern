import libtcodpy as libtcod
from tavern.utils.tcod_wrapper import Console
from tavern.view.show_console import display_highlighted_text, display_text


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

    def set_data(self, data):
        pass

    def update(self, values):
        for child in self.children:
            child.update(values)


class RootComponent(Component):
    """ A component with an attached console."""
    def __init__(self, x, y, w, h, title, children):
        super(RootComponent, self).__init__(x, y, w, h, False, children)
        self.console = Console(x, y, w, h)
        self.title = title

    def deactivate(self):
        libtcod.console_delete(self.console.console)

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

    def set_data(self, data):
        for child in self.children:
            child.set_data(data)


class TextBlocComponent(Component):
    def __init__(self, x, y, w, text):
        super(TextBlocComponent, self).__init__(x, y, w)
        self.text = text

    def display(self, console):
        libtcod.console_print_rect(console, self.x, self.y,
                                   self.w, 0, self.text)


class DynamicTextComponent(Component):
    def __init__(self, x, y, centered, source):
        super(DynamicTextComponent, self).__init__(x, y)
        self.centered = centered
        self.source = source
        self.text = ''

    def set_data(self, data):
        self.data = data
        self.text = data.get(self.source, '')

    def display(self, console):
        display_text(console, self.text, self.x, self.y)


class RowsComponent(Component):
    def __init__(self, x, y, w=0, h=0, is_selectable=False, contents=None):
        super(RowsComponent).__init__(x, y, w, h, is_selectable)
        if contents is None:
            contents = []
        self.contents = contents
        self.compute_widths()
        self.buid_rows()

    def compute_widths(self):
        lens = [(len(col) for col in row) for row in self.contents]
        self.widths = [max(sizes) for sizes in lens]

    def build_rows(self):
        for idx, c in enumerate(self.contents):
            self.children.append(ColumnedLine(self.x, self.y + idx,
                                              self.is_selectable,
                                              self.widths, c))

    def display(self, console):
        for c in self.children:
            c.display(console)


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
