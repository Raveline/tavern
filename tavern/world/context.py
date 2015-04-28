from tavern.world.goods import DRINKS

WIDTH = 80
HEIGHT = 60


class Context(object):
    """A whole game context, containing the Tavern object,
    the available objects, the menus, etc."""
    def __init__(self):
        # Put initialization code here.
        self.width = WIDTH
        self.height = HEIGHT

    def to_context_dict(self):
        result = {}
        result['width'] = self.width
        result['height'] = self.height
        result['goods'] = {}
        result['goods']['supplies'] = DRINKS
        return result
