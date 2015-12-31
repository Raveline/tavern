import random
from tavern.world.objects.functions import Functions
from tavern.people.tasks.tasks import ImpossibleTask, Wandering, Walking
from tavern.people.tasks.tasks_patron import (
    Drinking, Ordering, Leaving, Seating, StandingUp, ReserveSeat, OpenSeat,
    TableOrder, WaitForOrder, Eating)


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

    def __init__(self, char, level, race, name, examinable=False):
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
        self.examinable = examinable
        self.name = name

    def to_pos(self):
        return (self.x, self.y, self.z)

    def is_at_pos(self, pos):
        return self.to_pos() == pos

    def race_string(self):
        return races_to_string[self.race]

    def add_activity(self, activity):
        if self.current_activity is not None:
            self.activity_list.append(activity)
        else:
            self.current_activity = activity

    def add_activities(self, activities):
        for act in activities:
            self.add_activity(act)

    def add_walking_then_or(self, world_map, dest, then_acts, or_acts=None):
        """Add a walking activity to a point, then the list of activity in
        [then], or, if the path is impossible, the [or] list."""
        try:
            walking = Walking(world_map, self, dest)
            self.add_activity(walking)
            self.add_activities(then_acts)
        except ImpossibleTask:
            if not or_acts:
                or_acts = [Wandering()]
            self.add_activities(or_acts)

    def tick(self, world):
        if not self.current_activity:
            self.find_activity(world)
        if self.current_activity:
            self.current_activity.tick(world.tavern_map, self)
            if self.current_activity.failed:
                # Empty the activity list
                for activity in self.activity_list:
                    activity.fail()
                self.activity_list = []
                self.current_activity.finished = True
            if self.current_activity.finished:
                self.current_activity = None
                self.next_activity(world.tavern_map)

    def move(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.z = pos[2]

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


class Patron(Creature):
    """A customer of the Tavern."""
    def __init__(self, creature_class, race, level, name, money, needs):
        super(Patron, self).__init__(
            creature_class_to_character[creature_class],
            level, race, name, True)
        self.creature_class = creature_class
        self.money = money
        self.needs = needs
        self.has_a_drink = False

    def money_for_drinks(self):
        """
        Deciding how to spend the Patron's money is a complex problem,
        probably NP actually.
        So we do this differently. If a customer has various needs,
        drinks cannot go above 20% of his budget. If he only wants
        to drink, however, his full budget will be devoted to this !
        """
        if self.needs.thirst == self.needs.sum_needs:
            return self.money
        else:
            return self.money * .20

    def class_string(self):
        return creature_class_to_string[self.creature_class]

    def leave(self, world_map):
        # We don't want to drink anymore, let's leave this place !
        exit = random.choice(world_map.entry_points)
        self.add_walking_then_or(world_map, exit, [Leaving()])

    def fetch_a_drink(self, world):
        # Let's try to find an open counter
        counter = world.tavern_map.find_closest_object(self.to_pos(),
                                                       Functions.ORDERING)
        if counter:
            self.add_walking_then_or(world.tavern_map, counter,
                                     [Ordering()])

    def find_a_seat_and(self, world_map, actions):
        available = world_map.service_list(Functions.SITTING)
        if available:
            pos = world_map.find_closest_in(available, self.to_pos())
            self.add_activity(ReserveSeat(pos))
            self.add_walking_then_or(world_map, pos,
                                     [Seating()] + actions +
                                     [StandingUp(), OpenSeat(pos)],
                                     [OpenSeat(pos), Wandering()])
        else:
            # For the moment, just wait
            self.add_activity(Wandering())

    def find_activity(self, world):
        if not self.needs.has_needs():
            self.leave(world.tavern_map)
        elif not self.has_a_drink:
            # We do not have a drink, we want to get one
            self.fetch_a_drink(world)
        elif self.has_a_drink:
            potential_order = world.goods.food[0]
            if self.needs.hunger > 0 and self.money >= potential_order.selling_price:
                self.find_a_seat_and(world.tavern_map,
                                     [Drinking(), TableOrder(potential_order),
                                      WaitForOrder(), Eating()])
            else:
                # We have a drink, we'd just like to seat
                self.find_a_seat_and(world.tavern_map, [Drinking()])
        else:
            self.add_activity(Wandering())

    def renounce(self, reason):
        # Called when a creature cannot find something in the tavern
        # and must leave. We put the thirst counter to 0 so it will go.
        self.needs.cancel_needs()

    def __str__(self):
        basic_display = "%s --- %s %s" %\
            (self.name, races_to_string[self.race],
             creature_class_to_string[self.creature_class])
        return ' --- '.join([basic_display, super(Patron, self).__str__()])
