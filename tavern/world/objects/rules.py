class Rule(object):
    def check(self, world, x, y):
        pass

    def get_error_message(self):
        return self.error_message


class RoomsRule(Rule):
    """This rule specify an object has to be put in some
    specific rooms."""
    def __init__(self, rooms):
        self.rooms = rooms

    def check(self, world_map, x, y):
        room_type = world_map.get_room_at(x, y)
        return room_type in self.rooms

    def get_error_message(self):
        return "Can only be put in certain rooms"


class NotWallRule(Rule):
    def check(self, world_map, x, y):
        tile = world_map.tiles[y][x]
        if tile.wall:
            self.error_message = 'Cannot put this object on a wall.'
            return False
        return True


class DefaultRule(Rule):
    """The default position rule, that makes sure
    the tile is built, that there is not already an object."""
    def check(self, world_map, x, y):
        tile = world_map.tiles[y][x]
        if tile.tile_object is not None:
            self.error_message = 'There is already an object here.'
            return False
        elif not tile.built:
            self.error_message = 'The are is not built.'
            return False
        return True


class OrRule(Rule):
    """A metarule, that says that one of two
    rules must be true."""
    def __init__(self, one, two):
        self.one = one
        self.two = two

    def check(self, world_map, x, y):
        return (self.one.check(world_map, x, y) or
                self.two.check(world_map, x, y))


class NextToWallRule(Rule):
    """Only valid is next to a wall."""
    def check(self, world_map, x, y):
        wall_neihgbours = [t for t in world_map.get_neighboring_for(x, y)
                           if t.wall]
        return len(wall_neihgbours) > 0


class ExteriorWallRule(Rule):
    """Only valid if the tile is a wall giving on the outside."""
    def check(self, world_map, x, y):
        return world_map.is_an_outside_wall(x, y)
