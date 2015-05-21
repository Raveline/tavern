import libtcodpy as tcod
import random

from tavern.utils import bus
from tavern.world.commands import AttendToCommand, OrderCommand, CreatureExit
from tavern.world.commands import ReserveSeat as ReserveCommand
from tavern.world.commands import AddTask, RemoveTask
from tavern.world.objects.functions import Functions
from tavern.world.goods import GoodsType


class ImpossibleTask(Exception):
    pass


class Task(object):
    def __init__(self, length=0):
        self.tick_time = 0
        self.length = length
        self.failed = False
        self.finished = False

    def tick(self, world_map, creature):
        self.tick_time += 1

    def check_length(self):
        if self.tick_time == self.length:
            self.finish()
            return True
        else:
            return False

    def call_command(self, command):
        bus.bus.publish({'command': command}, bus.WORLD_EVENT)

    def fail(self):
        self.failed = True

    def finish(self):
        self.finished = True


class Wandering(Task):
    """Fool around for 10 ticks."""
    def __init__(self, length=10):
        super(Wandering, self).__init__(length)

    def tick(self, world_map, creature):
        if not self.check_length():
            self.wander(world_map, creature)
        super(Wandering, self).tick(world_map, creature)

    def wander(self, world_map, creature):
        if random.randint(0, 2) == 0:
            x, y, z = random.choice(world_map.get_legit_moves_from(
                creature.x, creature.y, creature.z))
            creature.move(x, y, z)

    def __str__(self):
        return "Being idle"


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


class Serving(Task):
    SERVING_LENGTH = 100
    """As in serving people."""
    def __init__(self, nature, x, y, constant=False):
        super(Serving, self).__init__(Serving.SERVING_LENGTH)
        self.nature = nature
        self.x = x
        self.y = y
        # Should this task always be here ? (object requiring constant
        # attendance, e.g.)
        self.constant = constant

    def start_serving(self):
        command = AttendToCommand(self.nature, (self.x, self.y))
        self.call_command(command)

    def stop_serving(self):
        command = AttendToCommand(self.nature, (self.x, self.y), True)
        self.call_command(command)

    def tick(self, world_map, creature):
        if self.check_length():
            self.stop_serving()
        else:
            if self.tick_time == 0:
                self.start_serving()
            super(Serving, self).tick(world_map, creature)

    def keep_task_if_constant(self):
        if self.constant:
            command = AddTask(self.nature, self.x, self.y,
                              Serving(self.nature, self.x, self.y, True))
            self.call_command(command)

    def finish(self):
        super(Serving, self).finish()
        self.keep_task_if_constant()

    def fail(self):
        super(Serving, self).fail()
        self.stop_serving()
        self.keep_task_if_constant()

    def __str__(self):
        return "Serving customers"


class Walking(Task):
    def __init__(self, world_map, creature, x, y):
        super(Walking, self).__init__()
        self.dest_x = x
        self.dest_y = y
        self.compute_path(world_map, creature)

    def compute_path(self, world_map, creature):
        if self.dest_x != creature.x or self.dest_y != creature.y:
            self.path = world_map.path_from_to(creature.x, creature.y,
                                               self.dest_x, self.dest_y)
            self.path_length = tcod.path_size(self.path)
            if self.path_length == 0:
                self.fail()
                raise ImpossibleTask('No path to %d, %s' % (self.dest_x,
                                                            self.dest_y))
            # The tick time MUST be reset, in case we recompute path
            # during the task.
            self.tick_time = 0
        else:
            self.path = None
            self.path_length = 0
            self.finish()

    def tick(self, world_map, creature):
        if self.tick_time < self.path_length:
            x, y = tcod.path_get(self.path, self.tick_time)
            if not world_map.tiles[y][x].is_walkable():
                # Path is not walkable anymore !
                # We'll try to rebuild it...
                self.compute_path(world_map, creature)
            else:
                creature.move(x, y, 0)
        else:
            self.finish()
        super(Walking, self).tick(world_map, creature)

    def finish(self):
        super(Walking, self).finish()
        self.free_path()

    def fail(self):
        super(Walking, self).fail()
        self.free_path()

    def free_path(self):
        if self.path:
            tcod.path_delete(self.path)
            self.path = None

    def __str__(self):
        return "Going somewhere"


class TableOrder(object):
    """Customer will wait for a waiter to come and take
    his order."""
    ORDER_WAITING = 100

    def __init__(self, order):
        super(Serving, self).__init__(TableOrder.ORDER_WAITING)
        self.order_taken = False
        self.order = order

    def emit_order_task(self, world_map, creature):
        self.order_task = TakeOrder(self.creature)
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

    def tick(self, world_map, creature):
        if self.served:
            self.finish()


class TakeOrder(Task):
    def __init__(self, creature):
        self.creature = creature

    def tick(self, world_map, creature):
        # We interact with the target creature task, create a new task...
        ordering = self.creature.current_task
        ordered = ordering.order
        command = AddTask(Functions.COOKING, None, None,
                          PrepareFood(ordered, self.creature))
        self.call_command(command)
        ordering.order_taken = True
        # ... and we are done !
        self.finish()


class PrepareFood(Task):
    def __init__(self, meal, destination):
        self.meal = meal
        self.destination = destination

    def tick(self, world_map, creature):
        workshop = world_map.find_closest_object(creature.x, creature.y,
                                                 Functions.WORKSHOP)
        oven = world_map.find_closest_object(creature.x, creature.y,
                                             Functions.COOKING)
        if workshop and oven:
            creature.add_walking_then_or(world_map, workshop[0], workshop[1],
                                         [CutFood()])
            creature.add_walking_then_or(world_map, oven[0], oven[1],
                                         [CookFood(),
                                          CreateMeal(self.meal,
                                                     self.destination)])
            self.finish()
        else:
            self.fail()


class CutFood(Task):
    def __init__(self):
        super(CutFood, self).__init__(length=10)

    def tick(self, world, creature):
        # TODO : Consomation of ingredient
        self.check_length()


class CookFood(Task):
    def __init__(self):
        super(CookFood, self).__init__(length=15)

    def tick(self, world, creature):
        self.check_length()


class CreateMeal(Task):
    def __init__(self, meal, destination):
        self.meal = meal
        self.destination = destination

    def tick(self, world_map, creature):
        command = AddTask(Functions.DELIVERING, creature.x, creature.y,
                          DeliverTask(self.meal, self.destination))
        self.call_command(command)
        self.finish()


class DeliverTask(Task):
    def __init__(self, meal, destination):
        self.meal = meal
        self.destination = destination

    def tick(self, world_map, creature):
        creature.add_walking_then_or(world_map, self.destination.x,
                                     self.destination.y,
                                     [ServeMealTask(self.destination)])
        self.finish()

    def __str__(self):
        return "Picking up a meal"


class ServeMealTask(Task):
    def __init__(self, destination):
        self.destination = destination

    def tick(self, world_map, creature):
        self.destination.current_task.served = True
        self.finish()

    def __str__(self):
        return "Serving customer"
