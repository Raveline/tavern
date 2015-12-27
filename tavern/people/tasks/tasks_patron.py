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
    def __init__(self, pos):
        self.pos = pos
        super(ReserveSeat, self).__init__()

    def tick(self, world_map, creature):
        self.finish()

    def finish(self):
        command = ReserveCommand(self.pos)
        self.call_command(command)
        super(ReserveSeat, self).finish()

    def __str__(self):
        return "Picking a seat"


class OpenSeat(Task):
    def __init__(self, pos):
        self.pos = pos
        super(OpenSeat, self).__init__()

    def tick(self, world_map, creature):
        self.finish()

    def finish(self):
        command = ReserveCommand(self.pos, True)
        self.call_command(command)
        super(OpenSeat, self).finish()

    def __str__(self):
        return "Leaving his seat"


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
        if (creature.to_pos()) in world_map.entry_points:
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
            if world_map.can_serve_at(Functions.ORDERING, creature.to_pos()):
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
        order_task = TakeOrder(creature)
        command = AddTask(Functions.ORDER_TAKING, creature.to_pos(),
                          order_task)
        self.reverse = RemoveTask(Functions.ORDER_TAKING, creature.to_pos(),
                                  order_task)
        self.call_command(command)

    def tick(self, world_map, creature):
        if self.tick_time == 0:
            self.emit_order_task(world_map, creature)
        else:
            if self.order_taken:
                self.finish()
            else:
                if self.tick_time > self.length:
                    # We're pissed, we don't want to stay here anymore !
                    creature.needs.cancel_needs()
                    self.fail()
        super(TableOrder, self).tick(world_map, creature)

    def fail(self):
        super(TableOrder, self).fail()
        self.call_command(self.reverse)

    def __str__(self):
        return "Waiting to order"


class WaitForOrder(Task):
    MAX_WAIT = 400
    """Customer is waiting for his order to arrive."""
    def __init__(self):
        self.served = False
        super(WaitForOrder, self).__init__(length=WaitForOrder.MAX_WAIT)

    def tick(self, world_map, creature):
        if self.served:
            self.finish()
        if self.tick_time > self.length:
            creature.renounce("%s waited too long to be served food."
                              % str(creature))
            self.fail()
        super(WaitForOrder, self).tick(world_map, creature)

    def __str__(self):
        return "Waiting for his meal"
