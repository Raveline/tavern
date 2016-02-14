from tavern.people.tasks.tasks import Wandering
from tavern.world.objects.functions import Functions
from tavern.people.characters import Creature
from tavern.people.tasks.employee import EndTask


class Job(object):
    def __init__(self, name, functions):
        self.name = name
        self.functions = functions


TAVERN_WAITER = [Functions.ORDERING,
                 Functions.ORDER_TAKING, Functions.DELIVERING]
WAITER = Job('Waiter', TAVERN_WAITER)
TAVERN_COOK = [Functions.WORKSHOP, Functions.COOKING]
COOK = Job('Cook', TAVERN_COOK)
TAVERN_CLEANER = [Functions.CLEANING]
CLEANER = Job('Cleaner', TAVERN_CLEANER)
TAVERN_BREWER = [Functions.BREWING]
BREWER = Job('Brewer', TAVERN_BREWER)
TAVERN_MERCHANT = [Functions.SELLING]
MERCHANT = Job('Merchant', TAVERN_MERCHANT)
PUBLICAN = Job('Publican', TAVERN_WAITER)

JOBS = {j.name: j for j in [WAITER, COOK, CLEANER, BREWER, MERCHANT]}


class Employee(Creature):
    """An employee of the tavern."""
    def __init__(self, x, y, z, job, name, character='e'):
        """
        The "functions" parameters indicate what kind of activities this
        employee is susceptible to fill.
        """
        super(Employee, self).__init__(character, 1, Creature.EMPLOYEE, name)
        self.x = x
        self.y = y
        self.z = z
        self.job = job

    def find_activity(self, world):
        for f in self.job.functions:
            if world.tavern.tasks.has_task(f):
                # For the moment, let's take the last opened task...
                task = world.tavern.tasks.start_task(f, self)
                if task[0] is not None:
                    position = task[0]
                    task = task[1]
                    # TODO : Replace this "Wandering" taks by a Resting one.
                    self.add_walking_then_or(world.tavern_map, position,
                                             [task, EndTask(f, position, task)])
                else:
                    self.add_activities([task[1],
                                         EndTask(f, None, task[1])])
                return
        # If we are here, we didn't find a single task to do
        # For the moment, just wander !
        self.add_activity(Wandering())


class Publican(Employee):
    """The avatar of the player."""
    def __init__(self, x, y, z):
        super(Publican, self).__init__(x, y, z, PUBLICAN,
                                       'You !', '@')


def make_recruit_out_of(creature, profile):
    employee = Employee(creature.x, creature.y, creature.z, profile,
                        creature.name)
    # Should make sure every tasks are finished.
    # Free the paths, open seats...
    if creature.current_activity:
        creature.current_activity.finish()
    for t in creature.activity_list:
        t.finish()
    return employee
