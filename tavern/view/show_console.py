import libtcodpy as libtcod
import tavern.world.world as world

materials_to_colors = {world.WOOD: libtcod.darker_sepia}


def __get_color_scale():
    return libtcod.color_gen_map([libtcod.dark_grey, libtcod.darkest_grey],
                                 [0, 200])


map_background_scale = __get_color_scale()


def display(grid, console):
    for y in range(60):
        for x in range(80):
            tile = grid[y][x]
            char = tile_to_char(tile)
            back = tile_to_colors(tile)
            libtcod.console_put_char_ex(console, x, y, char, libtcod.white, back)


def print_selection(console, receiver):
    display_list = receiver.get_selected_tiles()
    for (x, y) in display_list:
        x_, y_ = receiver.global_to_local(x, y)
        print_char(console, 'x', x_, y_, libtcod.yellow)


def display_text(console, text, x=0, y=0):
    libtcod.console_print(console, x, y, text)


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
