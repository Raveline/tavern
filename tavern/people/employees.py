from tavern.people.tasks.tasks import Wandering
from tavern.world.objects.functions import Functions
from tavern.people.characters import Creature


TAVERN_WAITER = [Functions.ORDERING, Functions.WORKSHOP, Functions.COOKING,
                 Functions.ORDER_TAKING, Functions.DELIVERING]


class Employee(Creature):
    """An employee of the tavern."""
    def __init__(self, x, y, z, functions, character='e'):
        """
        The "functions" parameters indicate what kind of activities this
        employee is susceptible to fill.
        """
        super(Employee, self).__init__(character, 1, Creature.EMPLOYEE)
        self.x = x
        self.y = y
        self.z = z
        self.functions = functions

    def find_activity(self, world_map):
        # For the moment, just wander !
        for f in self.functions:
            tasks = world_map.employee_tasks[f]
            if tasks:
                # For the moment, let's take the last opened task...
                task = tasks.pop()
                if task[0] is not None:
                    position = task[0]
                    task = task[1]
                    # TODO : Replace this "Wandering" taks by a Resting one.
                    self.add_walking_then_or(world_map, position,
                                             [task, Wandering()])
                else:
                    self.add_activity(task[1])
                return
        # If we are here, we didn't find a single task to do
        self.add_activity(Wandering())


class Publican(Employee):
    """The avatar of the player."""
    def __init__(self, x, y, z):
        super(Publican, self).__init__(x, y, z, [Functions.ORDERING], '@')

    def __str__(self):
        return ' --- '.join(["You", super(Publican, self).__str__()])


def make_recruit_out_of(creature, profile):
    employee = Employee(creature.x, creature.y, creature.z,
                        profile)
    # Should make sure every tasks are finished.
    # Free the paths, open seats...
    if creature.current_activity:
        creature.current_activity.finish()
    for t in creature.activity_list:
        t.finish()
    return employee
