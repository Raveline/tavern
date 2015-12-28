from groggy.events.bus import bus
from tavern.events.events import STATUS_EVENT
from tavern.world.objects.functions import Functions


class Command(object):
    """A simple implementation of Command pattern.
    """
    def execute(self, obj):
        pass


class AttendToCommand(Command):
    """This command let us known when an employee has begun or stopped
    working at a given post. We update the world accordingly."""
    def __init__(self, nature, pos, stop=False):
        self.nature = nature
        self.pos = pos
        self.stop = stop

    def execute(self, world):
        tav = world.tavern_map
        # A serving employee is attending to one or more object
        # (e.g., a counter). We need to flag the tiles NEXT to this object
        # as places where the service is available.
        tiles_next_to = tav.get_immediate_neighboring_coords(self.pos)
        for x, y, z in tiles_next_to:
            if tav.tiles[z][y][x].has_object_with_function(self.nature):
                dir_x = x - self.pos[0]
                dir_y = y - self.pos[1]
                to_serve_x = x + dir_x
                to_serve_y = y + dir_y
                to_serve_z = z
                as_position = (to_serve_x, to_serve_y, to_serve_z)
                if tav[as_position].is_walkable():
                    if self.stop:
                        tav.stop_service(self.nature, as_position)
                    else:
                        tav.open_service(self.nature, as_position)


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
                world.redispatch_store()
                world.cash += drink.selling_price
                self.creature.money -= drink.selling_price
                self.creature.has_a_drink = True
                bus.publish({'status': 'drinks',
                             'flag': True}, STATUS_EVENT)
                return
        if not drinks:
            bus.publish({'status': 'drinks',
                         'flag': False}, STATUS_EVENT)


class RemoveFromStore(Command):
    def __init__(self, goods, quantity, linked_task=None):
        self.goods = goods
        self.quantity = quantity
        self.linked_task = linked_task

    def execute(self, world):
        if world.store.can_take(self.goods, self.quantity):
            world.store.take(self.goods, self.quantity)
            world.redispatch_store()
        elif self.linked_task:
            self.linked_task.fail()


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
            world.redispatch_store()
        else:
            # Cancel a buy
            world.cash += self.money_value
            world.store.take(self.goods, self.quantity)
            world.redispatch_store()


class ReserveSeat(Command):
    def __init__(self, position, cancel=False):
        self.position = position
        self.cancel = cancel

    def execute(self, world):
        if self.cancel:
            world.tavern_map.open_service(Functions.SITTING, self.position)
        else:
            world.tavern_map.take_service(Functions.SITTING, self.position)


class AddTask(Command):
    def __init__(self, nature, position, task):
        self.nature = nature
        self.position = position
        self.task = task

    def execute(self, world):
        world.tasks.add_task(self.nature, self.position, self.task)


class RemoveTask(Command):
    def __init__(self, nature, position, task):
        self.position = position
        self.nature = nature
        self.task = task

    def execute(self, world):
        world.tasks.remove_task(self.nature, self.position, self.task)
