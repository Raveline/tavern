class Command(object):
    """A simple implementation of Command pattern.
    """
    def execute(self, obj):
        pass


class AttendToCommand(object):
    """This command let us known when an employee has begun or stopped
    working at a given post. We update the world accordingly."""
    def __init__(self, nature, position, stop=False):
        self.nature = nature
        self.x, self.y = position[0], position[1]
        self.stop = stop

    def execute(self, world):
        tav = world.tavern_map
        to_tag = [(x, y) for (x, y) in
                  tav.get_immediate_neighboring_coords(self.x, self.y)
                  if tav.tiles[y][x].has_object_with_function(self.nature)]
        for x, y in to_tag:
            if self.stop:
                tav.attended_objects_coords[self.nature].remove((x, y))
            else:
                tav.attended_objects_coords[self.nature].append((x, y))


class BuyCommand(object):
    def __init__(self, goods, quantity, cancel=False):
        self.goods = goods
        self.quantity = abs(quantity)
        self.money_value = goods.buying_price
        self.cancel = cancel

    def execute(self, world):
        if not self.cancel:
            # Do the buy
            world.cash -= self.money_value
            world.store.add(self.goods, self.quantity)
        else:
            # Cancel a buy
            world.cash += self.money_value
            world.store.take(self.goods, self.quantity)
