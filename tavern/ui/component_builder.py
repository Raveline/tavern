from tavern.utils import bus
from tavern.ui.components import (
    StaticText, TextBloc, RowsComponent, DynamicText, RootComponent,
    Button, Ruler, NumberPicker, Line, ComponentException)


def build_menu(context, menu_description, root=False):
    """
    Build a menu state.

    param context: A dict with context on the dispay
    type context: Dict
    param menu_description: The dict containing the menu description
    type menu_description : Dict
    """
    children = None
    if root:
        _, _, w, _ = read_dimensions(context, menu_description)
        context['parent_width'] = w
    if menu_description.get('children'):
        children = []
        for elem in menu_description['children']:
            children += (build_menu(context, elem))
    return build_component(context, menu_description, children, root)


def build_component(context, comp_desc, children=None, root=False):
        component = None
        x, y, w, h = read_dimensions(context, comp_desc)
        if comp_desc.get('eat_line', True):
            context['last_y'] = y
        is_selectable = comp_desc.get('selectable', False)
        comp_type = comp_desc.get('type')
        if root:
            title = comp_desc.get('title', '')
            component = RootComponent(x, y, w, h, title, children)
            return component
        elif comp_type == 'TextBloc':
            content = comp_desc.get('content', '')
            component = TextBloc(x, y, w, content)
        elif comp_type == 'StaticText':
            content = comp_desc.get('content', '')
            component = StaticText(x, y, content)
        elif comp_type == 'RowsComponent':
            content = comp_desc.get('content', '[]')
            component = RowsComponent(x, y, w, h, is_selectable, content)
        elif comp_type == 'Line':
            component = Line(x, y, w)
        elif comp_type == 'DynamicText':
            content = comp_desc.get('content')
            is_centered = comp_desc.get('centered', False)
            source = comp_desc.get('source', None)
            component = DynamicText(x, y, is_centered, source)
        elif comp_type == 'Button':
            text = comp_desc.get('text')
            event = comp_desc.get('event')
            event_type = comp_desc.get('even_type')
            component = Button(x, y, w, text, event, event_type)
        elif comp_type == 'Ruler':
            source = comp_desc.get('source')
            component = Ruler(x, y, w, source)
        elif comp_type == 'NumberPicker':
            source = comp_desc.get('source')
            component = NumberPicker(x, y, source)
        elif comp_type == 'Foreach':
            source = comp_desc.get('source').split('.')
            iterable = context
            for path in source:
                iterable = iterable[path]
            components = []
            do_desc = comp_desc.get('do')
            for elem in iterable:
                for to_do in do_desc:
                    source_builder = to_do.get('source_builder')
                    if source_builder:
                        to_do['source'] = '.'.join([str(elem), source_builder])
                    else:
                        to_do['source'] = str(elem)
                        if to_do.get('type') == 'StaticText':
                            to_do['content'] = to_do['source']
                    components += build_component(context, to_do)
            return components
        if children is not None:
            component.set_children(children)
        return [component]


def read_dimensions(context, tree):
    template = tree.get('template')
    if template:
        if template.startswith('centered'):
            # centered template with a padding
            try:
                padding = int(template[len('centered '):])
                padding_percent = padding / 100.0
            except ValueError:
                raise ComponentException('Centered template must be followed'
                                         ' by an integer giving the padding'
                                         ' percentage. E.g., "centered 10"')
            width = context.get('width')
            height = context.get('height')
            x = int(width * padding_percent)
            y = int(height * padding_percent)
            w = width - (2 * x)
            h = height - (2 * y)
    else:
        x = tree.get('x')
        y = tree.get('y', context.get('last_y', 0) + 1)
        w = tree.get('w', 0)
        if isinstance(w, str):
            # Width has been given in percentage. Convert.
            percent = int(w[:w.find('%')]) / 100.0
            parent_width = context.get('parent_width')
            w = int(percent * parent_width)
        h = tree.get('h', 0)
    return x, y, w, h


def make_textbox(x, y, w, h, title, text):
    tbc = TextBloc(1, 1, w - 1, text)
    return RootComponent(x, y, w, h, title, [tbc])


def make_questionbox(x, y, w, h, title, text, from_state, event_yes,
                     event_type):
    tbc = TextBloc(1, 1, w - 2, text)
    yes = Button(1, h - 3, w - 2, 'Yes', event_yes, event_type)
    no = Button(1, h - 2, w - 2, 'No', from_state, bus.PREVIOUS_STATE)
    return RootComponent(x, y, w, h, title, [tbc, yes, no])
