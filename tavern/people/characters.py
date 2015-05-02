import random
from tavern.world.objects import Rooms, Functions
from tavern.people.tasks import Walking, Wandering, Serving


class Creature(object):
    """The abstract notion of a living thing."""
    COLOR_EMPLOYEE = 0
    COLOR_ELVEN = 1
    COLOR_DWARVES = 2
    COLOR_HUMAN = 3

    def __init__(self, char, level, color):
        # The character that will represent this creature
        self.char = char
        # The level of the creature, from 1 to 20
        self.level = level
        self.x = 0
        self.y = 0
        self.z = 0
        self.current_activity = None
        self.activity_list = []
        self.color = color

    def set_activity(self, activity):
        if self.current_activity is not None:
            self.activity_list.append(activity)
        else:
            self.current_activity = activity

    def tick(self, world_map):
        if not self.current_activity:
            self.find_activity(world_map)
        if self.current_activity:
            self.current_activity.tick(world_map, self)
            if self.current_activity.failed:
                print("TASK FAILED !!!")
                # Empty the activity list
                self.activity_list = []
                self.current_activity.finished = True
            if self.current_activity.finished:
                print("Finished !")
                self.current_activity = None
                self.find_activity(world_map)

    def move(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def find_activity(self, world_map):
        # If we had a to-do list, go on the next item
        print("Looking for activity in %s" % self.current_activity)
        if self.activity_list:
            self.current_activity = self.activity_list[-1]
            self.activity_list = self.activity_list[:-1]

    def add_activity(self, activity):
        self.activity_list.append(activity)

    def __str__(self):
        if self.current_activity:
            return str(self.current_activity)
        else:
            return "Doing nothing"


class Publican(Creature):
    """The avatar of the player."""
    def __init__(self, x, y):
        super(Publican, self).__init__('@', 1, Creature.COLOR_EMPLOYEE)
        self.x = x
        self.y = y

    def __str__(self):
        return ' --- '.join(["You", super(Publican, self).__str__()])

    def find_activity(self, world_map):
        super(Publican, self).find_activity(world_map)
        if self.current_activity:
            return
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
                print("FOUND COUNTER. GOING FOR IT")
                # We have a counter ! Now let us find the tile that is the
                # closest to a wall around this counter.
                x, y = world_map.find_closest_to_wall_neighbour(counter[0],
                                                                counter[1])
                print("Going to %d, %d" % (x, y))
                self.set_activity(Walking(world_map, self, x, y))
                self.set_activity(Serving(self, Functions.ORDERING))
            else:
                print("COULD NOT FIND COUNTER; WILL WANDER")
                self.add_activity(Wandering())
