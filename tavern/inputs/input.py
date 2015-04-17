import libtcodpy as tcod


class Inputs(object):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    ENTER = 4
    ESCAPE = 5

    def __init__(self, bus):
        self.mouse = tcod.Mouse()
        self.key = tcod.Key()
        self.quit = False
        self.bus = bus

    def poll(self):
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS
                                 | tcod.EVENT_MOUSE,
                                 self.key, self.mouse)
        self.poll_keys()
        self.poll_mouse()

    def poll_keys(self):
        if self.key.vk == tcod.KEY_ESCAPE:
            self.bus.publish(Inputs.ESCAPE, 0)
        if self.key.vk == tcod.KEY_UP:
            self.bus.publish(Inputs.UP, 0)
        if self.key.vk == tcod.KEY_DOWN:
            self.bus.publish(Inputs.DOWN, 0)
        if self.key.vk == tcod.KEY_LEFT:
            self.bus.publish(Inputs.LEFT, 0)
        if self.key.vk == tcod.KEY_RIGHT:
            self.bus.publish(Inputs.RIGHT, 0)
        if self.key.vk == tcod.KEY_ENTER:
            self.bus.publish(Inputs.ENTER, 0)
        if self.key.vk == tcod.KEY_END:
            self.bus.publish('quit', 4)
        if self.key.c >= 65 and self.key.c <= 122:
            self.bus.publish(chr(self.key.c), 0)

    def poll_mouse(self):
        pass
