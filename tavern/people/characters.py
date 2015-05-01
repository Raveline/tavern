import random


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
        self.color = color
        # For how long did this creature kept doing the same thing ?
        self.current_activity_tick_time = 0

    def set_activity(self, activity):
        self.activity = activity

    def tick(self, world_map):
        if self.current_activity_tick_time > 3:
            self.wander(world_map)
        self.current_activity_tick_time += 1

    def wander(self, world_map):
        x, y, z = random.choice(world_map.get_legit_moves_from(
            self.x, self.y, self.z))
        self.move(x, y, z)

    def move(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Employee(Creature):
    """An employee of the Tavern."""
    IDLE = 0
    SERVING_BAR = 1


class Publican(Creature):
    """The avatar of the player."""
    def __init__(self, x, y):
        super(Publican, self).__init__('@', 1, Creature.COLOR_EMPLOYEE)
        self.x = x
        self.y = y
