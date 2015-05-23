from tavern.people.tasks.tasks import Task
from tavern.world.commands import AttendToCommand
from tavern.world.commands import AddTask
from tavern.world.objects.functions import Functions


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


class TakeOrder(Task):
    def __init__(self, creature):
        self.creature = creature
        super(TakeOrder, self).__init__()

    def tick(self, world_map, creature):
        # We interact with the target creature task, create a new task...
        ordering = self.creature.current_activity
        if hasattr(ordering, 'order'):
            ordered = ordering.order
            command = AddTask(Functions.COOKING, None, None,
                              PrepareFood(ordered, self.creature))
            self.call_command(command)
            ordering.order_taken = True
            # ... and we are done !
            self.finish()
        else:
            self.fail()


class PrepareFood(Task):
    def __init__(self, meal, destination):
        self.meal = meal
        self.destination = destination
        super(PrepareFood, self).__init__()

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
        super(CreateMeal, self).__init__()

    def tick(self, world_map, creature):
        command = AddTask(Functions.DELIVERING, creature.x, creature.y,
                          DeliverTask(self.meal, self.destination))
        self.call_command(command)
        self.finish()


class DeliverTask(Task):
    def __init__(self, meal, destination):
        self.meal = meal
        self.destination = destination
        super(DeliverTask, self).__init__()

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
        super(ServeMealTask, self).__init__()

    def tick(self, world_map, creature):
        if hasattr(self.destination.current_task, 'served'):
            self.destination.current_task.served = True
            self.finish()
        else:
            self.fail()

    def __str__(self):
        return "Serving customer"
