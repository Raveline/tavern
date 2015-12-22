import random

from groggy.events import bus
from tavern.world.objects.functions import Functions
from tavern.people.needs import Needs
from tavern.people.characters import CreatureClass, Creature, Patron
from tavern.world.names.proper import (
    human_language, elfish_language, dwarven_language)


races = [Creature.ELVEN,
         Creature.DWARVES,
         Creature.HUMAN]


races_to_names_generator = {Creature.ELVEN: elfish_language,
                            Creature.DWARVES: dwarven_language,
                            Creature.HUMAN: human_language}

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
        x, y, z = random.choice(self.tavern.tavern_map.entry_points)
        if random.randint(1, 10) == 1:
            creature_class = random.choice(classes)
        else:
            creature_class = CreatureClass.COMMON
        race = random.choice(races)
        level = random.randint(1, 3)
        money = random.randint(20, 40)
        thirst = random.randint(1, 3)
        hunger = random.randint(0, 1)
        gamble = 0  # Will be random.randint(0,10)
        sleep = 0   # Will be random.randint(0,0)
        needs = Needs(thirst, hunger, gamble, sleep)
        name = races_to_names_generator[race].generate()
        new_customer = Patron(creature_class, race, level, name, money, needs)
        new_customer.x = x
        new_customer.y = y
        new_customer.z = z
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
