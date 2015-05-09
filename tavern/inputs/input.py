import libtcodpy as tcod


class Inputs(object):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    ENTER = 5
    ESCAPE = 6
    SPACE = 7
    F1 = 56
    F2 = 57
    F3 = 58
    F4 = 59
    F5 = 60
    F6 = 61
    F7 = 62
    F8 = 63
    F9 = 64
    F10 = 65
    F11 = 66
    F12 = 67
    END = 100

    def __init__(self, bus):
        self.mouse = tcod.Mouse()
        self.key = tcod.Key()
        self.quit = False
        self.bus = bus

    def poll(self):
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
                                 self.key, self.mouse)
        self.poll_keys()
        self.poll_mouse()

    def poll_keys(self):
        input_value = keys.get(self.key.vk)
        if input_value:
            if input_value == Inputs.END:
                self.bus.publish('quit', 4)
            elif input_value:
                self.bus.publish(input_value, 0)
        else:
            if self.key.c >= 63 and self.key.c <= 122:
                self.bus.publish(chr(self.key.c), 0)

    def poll_mouse(self):
        pass


keys = {tcod.KEY_ESCAPE: Inputs.ESCAPE,
        tcod.KEY_UP: Inputs.UP,
        tcod.KEY_DOWN: Inputs.DOWN,
        tcod.KEY_LEFT: Inputs.LEFT,
        tcod.KEY_RIGHT: Inputs.RIGHT,
        tcod.KEY_ENTER: Inputs.ENTER,
        tcod.KEY_END: Inputs.END,
        tcod.KEY_SPACE: Inputs.SPACE,
        tcod.KEY_F1: Inputs.F1,
        tcod.KEY_F2: Inputs.F2,
        tcod.KEY_F3: Inputs.F3,
        tcod.KEY_F4: Inputs.F4,
        tcod.KEY_F5: Inputs.F5,
        tcod.KEY_F6: Inputs.F6,
        tcod.KEY_F7: Inputs.F7,
        tcod.KEY_F8: Inputs.F8,
        tcod.KEY_F9: Inputs.F9,
        tcod.KEY_F10: Inputs.F10,
        tcod.KEY_F11: Inputs.F11,
        tcod.KEY_F12: Inputs.F12}
