from groggy.events.bus import bus
from tavern.events.events import STATUS_EVENT
from tavern.world.objects.functions import Functions
from tavern.world.goods import sort_by_quality_and_price
from tavern.world.goods import sort_by_price


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
    def __init__(self, creature):
        self.creature = creature

    def find_best_suited_drink(self, drinks):
        """
        This is, in the big picture, a knapsack problem...
        Our solution here is a bit of a hack, but it should be "good enough".
        As long as a patron has enough money to drink the lowest
        potential quality drinks to quench his thirst, he will
        buy the best quality drink possible.
        """
        available_money = self.creature.money
        drinks_by_price = sort_by_price(drinks)
        drinks_by_quality = sort_by_quality_and_price(drinks)
        minimum_price = drinks_by_price[0].selling_price
        must_keep_amount = (minimum_price * self.creature.needs.thirst)
        if must_keep_amount < minimum_price:
            # Can't even afford the minimum drink
            return None
        if must_keep_amount >= available_money:
            # Has not enough (or just enough) to pay for
            # all the drinks he'd like to drink
            return [drinks_by_price[0]]
        else:
            max_price = available_money - (must_keep_amount - minimum_price)
            potential_drinks = [d for d in drinks_by_quality
                                if d.selling_price <= max_price]
            return potential_drinks

    def execute(self, world):
        # For now, we'll take the first available and affordable drink
        choices = self.find_best_suited_drink(world.goods.drinks)
        tavern = world.tavern
        if choices:
            for drink in choices:
                if tavern.store.can_take(drink, 1):
                    tavern.store.take(drink, 1)
                    tavern.redispatch_store()
                    tavern.cash += drink.selling_price
                    self.creature.money -= drink.selling_price
                    self.creature.has_a_drink = True
                    bus.publish({'status': 'drinks',
                                 'flag': True}, STATUS_EVENT)
                    return
            if not self.creature.has_a_drink:
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
            world.tavern.redispatch_store()
        elif self.linked_task:
            self.linked_task.fail()


class AddToStore(Command):
    def __init__(self, goods, quantity, linked_task=None):
        self.goods = goods
        self.quantity = quantity
        self.linked_task = linked_task

    def execute(self, world):
        if world.store.can_store(self.goods, self.quantity):
            world.store.add(self.goods, self.quantity)
            world.tavern.redispatch_store()
        else:
            bus.bus.publish('Not enough room to store %s' % self.goods)
            self.linked_task.fail()


class CreatureExit(Command):
    def __init__(self, creature):
        self.creature = creature

    def execute(self, world):
        # There is a small chance here the player recruit a character
        # just when he was leaving. So this would fail. Let's add a bit
        # of safety here.
        try:
            world.tavern.remove_creature(self.creature)
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
            world.tavern.cash -= self.money_value
            world.tavern.store.add(self.goods, self.quantity)
            world.tavern.redispatch_store()
        else:
            # Cancel a buy
            world.tavern.cash += self.money_value
            world.tavern.store.take(self.goods, self.quantity)
            world.tavern.redispatch_store()


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
