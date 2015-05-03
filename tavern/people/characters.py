import random
from tavern.world.objects import Rooms, Functions
from tavern.people.tasks import Walking, Wandering, Serving, Drinking, Ordering
from tavern.people.tasks import Leaving, Seating, StandingUp


class CreatureClass(object):
    """Here, Class is in the AD&D style meaning."""
    COMMON = 0   # Somebody that has a boring old job somewhere like you and me
    WARRIOR = 1  # A powerful sword, axe, or pointy thing wielder !
    PRIEST = 2   # An observer of the god, able to cure and help !
    WIZARD = 3   # A powercrazed maniac that shoots thunder with his hands !
    THIEF = 4    # Someone with a different conception of private property
    CRITIC = 5   # Everybody is one, but this one has power.

creature_class_to_character = {
    CreatureClass.COMMON: 'c',
    CreatureClass.WARRIOR: 'f',
    CreatureClass.PRIEST: 'p',
    CreatureClass.WIZARD: 'w',
    CreatureClass.THIEF: 't',
    CreatureClass.CRITIC: 'O'
}

creature_class_to_string = {
    CreatureClass.COMMON: 'Commoner',
    CreatureClass.WARRIOR: 'Warrior',
    CreatureClass.PRIEST: 'Priest',
    CreatureClass.WIZARD: 'Wizard',
    CreatureClass.THIEF: 'Thief',
    CreatureClass.CRITIC: 'Critic'
}


class Creature(object):
    """The abstract notion of a living thing."""
    EMPLOYEE = 0
    ELVEN = 1
    DWARVES = 2
    HUMAN = 3

    def __init__(self, char, level, race):
        # The character that will represent this creature
        self.char = char
        # The level of the creature, from 1 to 20
        self.level = level
        self.x = 0
        self.y = 0
        self.z = 0
        self.current_activity = None
        self.activity_list = []
        self.race = race

    def add_activity(self, activity):
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
                # Empty the activity list
                self.activity_list = []
                self.current_activity.finished = True
            if self.current_activity.finished:
                self.current_activity = None
                self.next_activity(world_map)

    def move(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def next_activity(self, world_map):
        # If we had a to-do list, go on the next item
        if self.activity_list:
            self.current_activity = self.activity_list[0]
            self.activity_list = self.activity_list[1:]
        else:
            self.find_activity(world_map)

    def __str__(self):
        if self.current_activity:
            return str(self.current_activity)
        else:
            return "Doing nothing"

races_to_string = {
    Creature.EMPLOYEE: 'Employee',
    Creature.HUMAN: 'Human',
    Creature.ELVEN: 'Elven',
    Creature.DWARVES: 'Dwarf'}


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


class Patron(Creature):
    """A customer of the Tavern."""
    def __init__(self, creature_class, race, level, money, thirst):
        super(Patron, self).__init__(
            creature_class_to_character[creature_class], level, race)
        self.creature_class = creature_class
        self.money = money
        self.thirst = thirst
        self.seated = False
        self.has_a_drink = False

    def leave(self, world_map):
        # We don't want to drink anymore, let's leave this place !
        exit_x, exit_y = random.choice(world_map.entry_points)
        self.add_activity(Walking(world_map, self, exit_x, exit_y))
        self.add_activity(Leaving())

    def fetch_a_drink(self, world_map):
        # Let's try to find an open counter
        counter = world_map.find_closest_object(self.x, self.y,
                                                Functions.ORDERING, False)
        if counter:
            self.add_activity(Walking(world_map, self, counter[0], counter[1]))
            self.add_activity(Ordering())

    def find_a_seat(self, world_map):
        available = world_map.available_seating
        if available:
            x, y = world_map.find_closest_in(available, self.x, self.y)
            world_map.take_seat(x, y)
            self.add_activity(Walking(world_map, self, x, y))
            self.add_activity(Seating())
            self.add_activity(Drinking())
            self.add_activity(StandingUp())
        else:
            # For the moment, just wait
            self.add_activity(Wandering())

    def find_activity(self, world_map):
        if self.thirst <= 0:
            self.leave(world_map)
        elif not self.has_a_drink:
            # We do not have a drink, we want to get one
            self.fetch_a_drink(world_map)
        elif self.has_a_drink:
            # We have a drink, we'd like to seat
            self.find_a_seat(world_map)
        else:
            self.add_activity(Wandering())

    def renounce(self, reason):
        # Called when a creature cannot find something in the tavern
        # and must leave. We put the thirst counter to 0 so it will go.
        self.thirst = 0

    def __str__(self):
        basic_display = "%s %s" %\
            (creature_class_to_string[self.creature_class],
             races_to_string[self.race])
        return ' --- '.join([basic_display, super(Patron, self).__str__()])
