import random

from tavern.utils import bus
from tavern.world.objects import Functions
from tavern.people.characters import CreatureClass, Creature, Patron


races = [Creature.ELVEN,
         Creature.DWARVES,
         Creature.HUMAN]

classes = [CreatureClass.WARRIOR,
           CreatureClass.PRIEST,
           CreatureClass.WIZARD,
           CreatureClass.THIEF]


class Customers(object):
    """A class to handle the clientele of a tavern.
    It will check when the tavern is ready to receive them,
    events to know when to create new customers."""
    def __init__(self, tavern):
        # Those flags let us know when a tavern is ready to
        # receive customers
        self.can_receive_customers = False
        self.tavern = tavern
        self.tick_counter = 0

    def can_receive(self):
        if self.can_receive_customers:
            return True
        has_counter = self.tavern.tavern_map.\
            list_tiles_with_objects(Functions.ORDERING)
        has_entry_point = self.tavern.tavern_map.entry_points
        if has_entry_point and has_counter:
            self.can_receive_customers = True
        return self.can_receive_customers

    def make_customer(self):
        x, y = random.choice(self.tavern.tavern_map.entry_points)
        if random.randint(1, 10) == 1:
            creature_class = random.choice(classes)
        else:
            creature_class = CreatureClass.COMMON
        race = random.choice(races)
        level = random.randint(1, 3)
        money = random.randint(20, 40)
        thirst = random.randint(1, 3)
        new_customer = Patron(creature_class, race, level, money, thirst)
        new_customer.x = x
        new_customer.y = y
        bus.bus.publish({'customer': new_customer}, bus.CUSTOMER_EVENT)

    def tick(self):
        self.tick_counter += 1
        if self.tick_counter > 100:
            if not self.can_receive():
                self.tick_counter = 0
                return
            prob = (self.tick_counter - 100) / 2
            if random.randint(1, 100) < prob:
                self.make_customer()
                if random.randint(1, 5) == 1:
                    self.tick_counter = 0
