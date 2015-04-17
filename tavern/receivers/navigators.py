from tavern.utils.geom import Frame
from tavern.inputs.input import Inputs
from tavern.utils import bus


class Scape(object):
    def __init__(self, w, h, world_frame):
        self.frame = Frame(0, 0, w, h)
        self.world_frame = world_frame
        self.compute_focus()

    def compute_focus(self):
        self.focusX = self.frame.w / 2
        self.focusY = self.frame.h / 2

    def receive(self, message):
        movy = 0
        movx = 0
        if message == Inputs.UP:
            movy = -1
        if message == Inputs.DOWN:
            movy = 1
        if message == Inputs.LEFT:
            movx = -1
        if message == Inputs.RIGHT:
            movx = 1
        if message == Inputs.ENTER:
            if self.selection:
                bus.bus.publish(self.selection, bus.AREA_SELECT)
                self.finish_select()
            else:
                self.enter_select()
        if movx != 0 or movy != 0:
            self.change_frame(movx, movy)
            if self.selection:
                self.move_select()

    def change_frame(self, x, y):
        self.frame.x += x
        self.frame.y += y
        self.frame.clip(self.world_frame)

    def change_focus(self, center):
        centerx = center.getX()
        centery = center.getY()
        minx = self.frame.x + self.focusX
        miny = self.frame.y + self.focusY
        maxx = minx
        maxy = miny
        if centerx < minx:
            self.frame.x -= (minx - centerx)
        if centery < miny:
            self.frame.y -= (miny - centery)
        if centerx > maxx:
            self.frame.x += (centerx - maxx)
        if centery > maxy:
            self.frame.y += (centery - maxy)
        self.frame.clip(self.world_frame)

    def enter_select(self):
        self.selection = Selection(self.getX(), self.getY())

    def move_select(self):
        self.selection.extends_to(self.getX(), self.getY())

    def finish_select(self):
        self.selection = None


class Selection(object):
    def __init__(self, x, y):
        self.initial_x = x
        self.initial_y = y
        self.x = x
        self.y = y
        self.x2 = x
        self.y2 = y

    def extends_to(self, x, y):
        if x < self.initial_x:
            self.x = x
            self.x2 = self.initial_x
        else:
            self.x = self.initial_x
            self.x2 = x
        if y < self.initial_y:
            self.y = y
            self.y2 = self.initial_y
        else:
            self.y = self.initial_y
            self.y2 = y

    def to_rect(self):
        return {'x': self.x,
                'y': self.y,
                'x2': self.x2,
                'y2': self.y2}

    def __str__(self):
        return 'x : %d, y : %d, x2 : %d, y2 : %d' % (self.x, self.y, self.x2, self.y2)


class Crosshair(Scape):
    def __init__(self, w, h, world_frame):
        self.crosshair = (0, 0)
        self.scape = Scape(w, h, world_frame)
        self.world_frame = world_frame
        self.compute_maximum()
        self.selection = None

    def compute_maximum(self):
        self.maxX = self.world_frame.w - (self.scape.frame.w / 2)
        self.maxY = self.world_frame.h - (self.scape.frame.h / 2)

    def receive(self, message):
        super(Crosshair, self).receive(message)

    def getX(self):
        return self.crosshair[0]

    def getY(self):
        return self.crosshair[1]

    def change_frame(self, x, y):
        self.crosshair = (self.getX() + x, self.getY() + y)
        self.scape.change_focus(self)

    def to_local(self):
        return self.getX() - self.scape.frame.x, self.getY() - self.scape.frame.y

    def rect_to_local(self):
        return (self.selection.x - self.scape.frame.x,
                self.selection.y - self.scape.frame.y,
                self.selection.x2 - self.scape.frame.x,
                self.selection.y2 - self.scape.frame.y)
