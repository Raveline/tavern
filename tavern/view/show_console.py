import libtcodpy as libtcod
from tavern.world.objects import Materials
from tavern.people.characters import Creature

materials_to_colors = {Materials.WOOD: libtcod.darker_sepia}


def __get_color_scale(first, last, size):
    return libtcod.color_gen_map([first, last],
                                 [0, size])


map_background_scale = __get_color_scale(libtcod.dark_grey,
                                         libtcod.darkest_grey, 200)
elvens_background_scale = __get_color_scale(libtcod.lighter_green,
                                            libtcod.darker_green, 20)
dwarvens_background_scale = __get_color_scale(libtcod.lighter_yellow,
                                              libtcod.darker_yellow, 20)
humans_background_scale = __get_color_scale(libtcod.lighter_azure,
                                            libtcod.darker_azure, 20)

race_to_scale = {Creature.ELVEN: elvens_background_scale,
                 Creature.DWARVES: dwarvens_background_scale,
                 Creature.HUMAN: humans_background_scale}


def display(grid, console):
    for y in range(60):
        for x in range(80):
            tile = grid[y][x]
            char = tile_to_char(tile)
            back = tile_to_colors(tile)
            libtcod.console_put_char_ex(console, x, y, char, libtcod.white, back)


def print_selection(console, receiver):
    display_list = receiver.get_selected_tiles()
    characters = receiver.get_characters()
    for (char, (x, y)) in zip(characters, display_list):
        x_, y_ = receiver.global_to_local(x, y)
        print_char(console, char, x_, y_, libtcod.yellow)


def display_creatures(console, creatures, func):
    """Display on the console a list of creatures whose coords will be
    put to local using the function given as parameter."""
    for c in creatures:
        x, y = func(c.x, c.y)
        if c.race == 0:
            color_front = libtcod.white
        else:
            color_picker = race_to_scale[c.race]
            color_front = color_picker[c.level]
        color_back = libtcod.console_get_char_background(console, x, y)
        to_display = c.char
        libtcod.console_put_char_ex(console, x, y,
                                    to_display, color_front, color_back)


def display_text(console, text, x=0, y=0):
    libtcod.console_print_ex(console, x, y,
                             libtcod.BKGND_SET, libtcod.LEFT, text)


def display_highlighted_text(console, text, x=0, y=0):
    previous_back = libtcod.console_get_default_background(console)
    previous_fore = libtcod.console_get_default_foreground(console)
    libtcod.console_set_default_background(console, libtcod.white)
    libtcod.console_set_default_foreground(console, libtcod.black)
    libtcod.console_print_ex(console, x, y, libtcod.BKGND_SET,
                             libtcod.LEFT, text)
    libtcod.console_set_default_background(console, previous_back)
    libtcod.console_set_default_foreground(console, previous_fore)


def print_char(console, char, x, y, foreground):
    libtcod.console_put_char_ex(console, x, y, char, libtcod.black, foreground)


def tile_to_colors(tile):
    back = libtcod.white
    if tile.wall:
        back = libtcod.black
    if not tile.built:
        back = map_background_scale[int((tile.background + 1) * 100)]
    else:
        back = materials_to_colors.get(tile.material, back)
    return back


def tile_to_char(tile):
    if tile.wall and tile.tile_object is None:
        return '#'
    elif tile.tile_object is not None:
        return tile.tile_object.character
    else:
        return ' '
