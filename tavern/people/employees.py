import random
from tavern.people.tasks import Walking, Serving, Wandering
from tavern.world.objects import Rooms, Functions
from tavern.people.characters import Creature


class Publican(Creature):
    """The avatar of the player."""
    def __init__(self, x, y):
        super(Publican, self).__init__('@', 1, Creature.EMPLOYEE)
        self.x = x
        self.y = y

    def __str__(self):
        return ' --- '.join(["You", super(Publican, self).__str__()])

    def find_activity(self, world_map):
        # Am I in the tavern ?
        tav = world_map.find_closest_room(self.x, self.y, Rooms.TAVERN)
        in_tavern = tav and (self.x, self.y) in tav
        if tav and not in_tavern:
            x, y = random.choice(tav)
            self.add_activity(Walking(world_map, self, x, y))
        elif in_tavern:
            # We want to find a counter to attend
            counter = world_map.find_closest_object(self.x, self.y,
                                                    Functions.ORDERING,
                                                    True)
            if counter:
                # We have a counter ! Now let us find the tile that is the
                # closest to a wall around this counter.
                x, y = world_map.find_closest_to_wall_neighbour(counter[0],
                                                                counter[1])
                self.add_activity(Walking(world_map, self, x, y))
                self.add_activity(Serving(Functions.ORDERING))
            else:
                self.add_activity(Wandering())


class Employee(Creature):
    """An employee of the tavern."""
    def __init__(self, x, y, z):
        super(Employee, self).__init__('e', 1, Creature.EMPLOYEE)
        self.x = x
        self.y = y
        self.z = z

    def find_activity(self, world_map):
        # For the moment, just wander !
        self.add_activity(Wandering())


def make_recruit_out_of(creature):
    employee = Employee(creature.x, creature.y, creature.z)
    # Should make sure every tasks are finished.
    # Free the paths, open seats...
    creature.current_activity.finish()
    for t in creature.activity_list:
        t.finish()
    return employee
