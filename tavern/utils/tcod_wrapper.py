import libtcodpy as libtcod


class Console(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.console = libtcod.console_new(w, h)

    def blit_on(self, dest):
        libtcod.console_blit(self.console, 0, 0, 0, 0,
                             dest, self.x, self.y)
