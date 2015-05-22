from tavern.people.tasks.tasks import Task
from tavern.people.tasks.tasks_employees import TakeOrder
from tavern.world.commands import OrderCommand, CreatureExit
from tavern.world.commands import ReserveSeat as ReserveCommand
from tavern.world.commands import AddTask, RemoveTask
from tavern.world.objects.functions import Functions
from tavern.world.goods import GoodsType


class ImpossibleTask(Exception):
    pass


class ReserveSeat(Task):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        super(ReserveSeat, self).__init__()

    def tick(self, world_map, creature):
        self.finish()

    def finish(self):
        command = ReserveCommand(self.x, self.y)
        self.call_command(command)
        super(ReserveSeat, self).finish()


class OpenSeat(Task):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        super(OpenSeat, self).__init__()

    def tick(self, world_map, creature):
        self.finish()

    def finish(self):
        command = ReserveCommand(self.x, self.y, True)
        self.call_command(command)
        super(OpenSeat, self).finish()


class Consuming(Task):
    """An abstract task for the consommation of a service"""
    def __init__(self, length):
        super(Consuming, self).__init__(length)

    def tick(self, world_map, creature):
        if self.check_length():
            self.after(creature)
        else:
            super(Consuming, self).tick(world_map, creature)

    def after(self):
        raise NotImplementedError('Consuming is an abstract class !')


class Drinking(Consuming):
    def __init__(self, length=20):
        super(Drinking, self).__init__(length)

    def after(self, creature):
        # Diminish the creature thirst
        creature.needs.thirst -= 1
        # Remove the creature drink carrying flag
        creature.has_a_drink = False

    def __str__(self):
        return "Drinking"


class Eating(Consuming):
    def __init__(self, length=50):
        super(Eating, self).__init__(length)

    def __str__(self):
        return "Eating"

    def after(self, creature):
        creature.needs.hunger = 0


class Leaving(Task):
    def tick(self, world_map, creature):
        if (creature.x, creature.y) in world_map.entry_points:
            self.call_command(CreatureExit(creature))
        else:
            # Uh oh... this should not happen !
            self.fail()
            print("UH OH CREATURE CANNOT EXIT !!!")

    def __str__(self):
        return "Leaving"


class Seating(Task):
    def tick(self, world_map, creature):
        # This is really just a placeholder, right now...
        self.finish()

    def __str__(self):
        return "Seating"


class StandingUp(Task):
    def tick(self, world_map, creature):
        self.finish()

    def __str__(self):
        return "Standing up"


class Ordering(Task):
    def __init__(self):
        self.order_placed = False
        super(Ordering, self).__init__()

    def tick(self, world_map, creature):
        # Waited waaaay to long to get served
        if not self.order_placed and self.tick_time > 10:
            self.fail()
            creature.renounce("%s waited too long for being served.")
        elif not self.order_placed:
            if world_map.can_serve_at(Functions.ORDERING,
                                      creature.x, creature.y):
                command = OrderCommand(self.pick_a_drink(creature), creature)
                self.call_command(command)
                self.order_placed = True
            else:
                # Simply wait
                super(Ordering, self).tick(world_map, creature)
        else:
            # Command was placed. The creature should have a drink.
            # We're done here !
            if creature.has_a_drink:
                self.finish()
            # If it does not, it means the creature could not order
            # or could not find something interesting to drink. Stop !
            else:
                self.fail()
                # Put the creature thirst to 0 so that it will leave the
                # building
                creature.renounce("%s cannot find anything to drink.")

    def pick_a_drink(self, creature):
        # Right now, everybody drinks classics drinks !
        return GoodsType.CLASSIC_DRINKS

    def __str__(self):
        return "Ordering a drink"


class TableOrder(Task):
    """Customer will wait for a waiter to come and take
    his order."""
    ORDER_WAITING = 100

    def __init__(self, order):
        super(TableOrder, self).__init__(TableOrder.ORDER_WAITING)
        self.order_taken = False
        self.order = order

    def emit_order_task(self, world_map, creature):
        self.order_task = TakeOrder(creature)
        command = AddTask(Functions.ORDER_TAKING, creature.x, creature.y,
                          self.order_task)
        self.call_command(command)

    def tick(self, world_map, creature):
        if self.tick_time == 0:
            self.emit_order_task(world_map, creature)
        else:
            if self.order_taken:
                self.finish()
            else:
                if self.tick_time > self.length:
                    self.fail()
        super(TableOrder, self).tick(world_map, creature)

    def fail(self):
        command = RemoveTask(Functions.ORDER_TAKING, self.order_task)
        self.call_command(command)


class WaitForOrder(Task):
    """Customer is waiting for his order to arrive."""
    def __init__(self):
        self.served = False
        super(WaitForOrder, self).__init__()

    def tick(self, world_map, creature):
        if self.served:
            self.finish()
