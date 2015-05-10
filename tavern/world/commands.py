from tavern.utils import bus


class Command(object):
    """A simple implementation of Command pattern.
    """
    def execute(self, obj):
        pass


class AttendToCommand(Command):
    """This command let us known when an employee has begun or stopped
    working at a given post. We update the world accordingly."""
    def __init__(self, nature, position, stop=False):
        self.nature = nature
        self.x, self.y = position[0], position[1]
        self.stop = stop

    def execute(self, world):
        tav = world.tavern_map
        # A serving employee is attending to one or more object
        # (e.g., a counter). We need to flag the tiles NEXT to this object
        # as places where the service is available.
        tiles_next_to = tav.get_immediate_neighboring_coords(self.x, self.y)
        for x, y in tiles_next_to:
            if tav.tiles[y][x].has_object_with_function(self.nature):
                dir_x = x - self.x
                dir_y = y - self.y
                to_serve_x = x + dir_x
                to_serve_y = y + dir_y
                if tav.tiles[to_serve_y][to_serve_x].is_walkable():
                    if self.stop:
                        tav.attended_objects_coords[self.nature].\
                            remove((to_serve_x, to_serve_y))
                    else:
                        tav.attended_objects_coords[self.nature].\
                            append((to_serve_x, to_serve_y))


class OrderCommand(Command):
    def __init__(self, drink_type, creature):
        self.drink_type = drink_type
        self.creature = creature

    def execute(self, world):
        # For now, we'll take the first available and affordable drink
        drinks = world.store.available_products_of_kind(self.drink_type)
        for drink in drinks:
            if drink.selling_price <= self.creature.money:
                world.store.take(drink, 1)
                world.cash += drink.selling_price
                self.creature.money -= drink.selling_price
                self.creature.has_a_drink = True
                bus.bus.publish({'status': 'drinks',
                                 'flag': True}, bus.STATUS_EVENT)
                return
        if not drinks:
            bus.bus.publish({'status': 'drinks',
                             'flag': False}, bus.STATUS_EVENT)


class CreatureExit(Command):
    def __init__(self, creature):
        self.creature = creature

    def execute(self, world):
        # There is a small chance here the player recruit a character
        # just when he was leaving. So this would fail. Let's add a bit
        # of safety here.
        try:
            world.remove_creature(self.creature)
        except:
            pass


class BuyCommand(Command):
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


class ReserveSeat(Command):
    def __init__(self, x, y, cancel=False):
        self.x = x
        self.y = y
        self.cancel = cancel

    def execute(self, world):
        if self.cancel:
            world.open_seat(self.x, self.y)
        else:
            world.take_seat(self.x, self.y)
