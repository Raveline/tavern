class Rule(object):
    def check(self, world, pos):
        pass

    def get_error_message(self):
        return self.error_message


class RoomsRule(Rule):
    """This rule specify an object has to be put in some
    specific rooms."""
    def __init__(self, rooms):
        self.rooms = rooms

    def check(self, world_map, pos):
        room_type, _ = world_map.get_room_at(pos)
        return room_type is not None and room_type in self.rooms

    def get_error_message(self):
        return "Can only be put in certain rooms"


class OnlyOneInRoomRule(Rule):
    """
    This rule makes sure there is not already an object with
    the given function.
    """
    def __init__(self, function):
        self.function = function

    def check(self, world_map, pos):
        _, tiles = world_map.get_room_at(pos)
        as_tiles = [world_map[pos] for pos in tiles]
        objects = [t.tile_object for t in as_tiles if t.tile_object is not None]
        objects_with_function = [o for o in objects
                                 if o.function == self.function]
        return not objects_with_function

    def get_error_message(self):
        return "Can only put one in each room"


class NotWallRule(Rule):
    def check(self, world_map, pos):
        tile = world_map[pos]
        if tile.wall:
            self.error_message = 'Cannot put this object on a wall.'
            return False
        return True


class DefaultRule(Rule):
    """The default position rule, that makes sure
    the tile is built, that there is not already an object."""
    def check(self, world_map, pos):
        tile = world_map[pos]
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

    def check(self, world_map, pos):
        return (self.one.check(world_map, pos) or
                self.two.check(world_map, pos))


class NextToWallRule(Rule):
    """Only valid is next to a wall."""
    def check(self, world_map, pos):
        wall_neihgbours = [t for t in world_map.get_neighboring_for(pos)
                           if t.wall]
        return len(wall_neihgbours) > 0


class ExteriorWallRule(Rule):
    """Only valid if the tile is a wall giving on the outside."""
    def check(self, world_map, pos):
        return world_map.is_an_outside_wall(pos)
