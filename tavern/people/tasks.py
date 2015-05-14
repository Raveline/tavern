import libtcodpy as libtcod
import random

from tavern.utils import bus
from tavern.world.commands import AttendToCommand, OrderCommand, CreatureExit
from tavern.world.objects import Functions
from tavern.world.goods import GoodsType


class Task(object):
    def __init__(self):
        self.tick_time = 0
        self.failed = False
        self.finished = False

    def tick(self, world_map, creature):
        self.tick_time += 1

    def call_command(self, command):
        bus.bus.publish({'command': command}, bus.WORLD_EVENT)

    def fail(self):
        self.failed = True

    def finish(self):
        self.finished = True


class Wandering(Task):
    """Fool around for 10 ticks."""
    def tick(self, world_map, creature):
        if self.tick_time <= 10:
            self.wander(world_map, creature)
        else:
            self.finish()
        super(Wandering, self).tick(world_map, creature)

    def wander(self, world_map, creature):
        if random.randint(0, 2) == 0:
            x, y, z = random.choice(world_map.get_legit_moves_from(
                creature.x, creature.y, creature.z))
            creature.move(x, y, z)

    def __str__(self):
        return "Being idle"


class ReserveSeat(Task):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def tick(self, world_map, creature):
        self.finish()

    def finish(self):
        command = ReserveSeat(self.x, self.y)
        self.call_command(command)
        super(ReserveSeat, self).finish()


class OpenSeat(Task):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def tick(self, world_map, creature):
        self.finish()

    def finish(self):
        command = ReserveSeat(self.x, self.y, True)
        self.call_command(command)
        super(OpenSeat, self).finish()


class Drinking(Task):
    def tick(self, world_map, creature):
        # For now, just drink during 20 ticks
        if self.tick_time >= 20:
            # And we're done
            self.finish(creature)
        super(Drinking, self).tick(world_map, creature)

    def finish(self, creature):
        super(Drinking, self).finish()
        # Diminish the creature thirst
        creature.thirst -= 1
        # Remove the creature drink carrying flag
        creature.has_a_drink = False

    def __str__(self):
        return "Drinking"


class Leaving(Task):
    def tick(self, world_map, creature):
        if (creature.x, creature.y) in world_map.entry_points:
            self.call_command(CreatureExit(creature))
        else:
            # Uh oh... this should not happen !
            self.fail()
            print("UH OH CREATURE CANNOT EXIT !!!")

    def __str__(self):
        return "Leaving"


class Seating(Task):
    def tick(self, world_map, creature):
        # This is really just a placeholder, right now...
        self.finish()

    def __str__(self):
        return "Seating"


class StandingUp(Task):
    def tick(self, world_map, creature):
        self.finish()

    def __str__(self):
        return "Standing up"


class Ordering(Task):
    def __init__(self):
        self.order_placed = False
        super(Ordering, self).__init__()

    def tick(self, world_map, creature):
        # Waited waaaay to long to get served
        if not self.order_placed and self.tick_time > 10:
            self.fail()
            creature.renounce("%s waited too long for being served.")
        elif not self.order_placed:
            if world_map.can_serve_at(Functions.ORDERING,
                                      creature.x, creature.y):
                command = OrderCommand(self.pick_a_drink(creature), creature)
                self.call_command(command)
                self.order_placed = True
            else:
                # Simply wait
                super(Ordering, self).tick(world_map, creature)
        else:
            # Command was placed. The creature should have a drink.
            # We're done here !
            if creature.has_a_drink:
                self.finish()
            # If it does not, it means the creature could not order
            # or could not find something interesting to drink. Stop !
            else:
                self.fail()
                # Put the creature thirst to 0 so that it will leave the
                # building
                creature.renounce("%s cannot find anything to drink.")

    def pick_a_drink(self, creature):
        # Right now, everybody drinks classics drinks !
        return GoodsType.CLASSIC_DRINKS

    def __str__(self):
        return "Ordering a drink"


class Serving(Task):
    """As in serving people."""
    def __init__(self, nature):
        super(Serving, self).__init__()
        self.nature = nature

    def start_serving(self, world_map, creature):
        command = AttendToCommand(self.nature, (creature.x, creature.y))
        bus.bus.publish({'command': command}, bus.WORLD_EVENT)

    def stop_serving(self, world_map, creature):
        command = AttendToCommand(self.nature, (creature.x, creature.y), True)
        bus.bus.publish({'command': command}, bus.WORLD_EVENT)

    def tick(self, world_map, creature):
        if self.tick_time == 0:
            self.start_serving(world_map, creature)
        # TODO : stop serving when the creature serving needs rest.
        super(Serving, self).tick(world_map, creature)

    def __str__(self):
        return "Serving customers"


class Walking(Task):
    def __init__(self, world_map, creature, x, y):
        super(Walking, self).__init__()
        self.path = world_map.path_from_to(creature.x, creature.y, x, y)
        self.path_length = libtcod.path_size(self.path)
        if self.path_length == 0:
            self.fail()

    def tick(self, world_map, creature):
        # Special check in case this failed at initialisation
        if not self.failed and self.tick_time < self.path_length:
            x, y = libtcod.path_get(self.path, self.tick_time)
            if not world_map.tiles[y][x].is_walkable():
                # Path is not walkable anymore !
                self.fail()
            else:
                creature.move(x, y, 0)
        else:
            self.finish()
        super(Walking, self).tick(world_map, creature)

    def finish(self):
        super(Walking, self).finish()
        libtcod.path_delete(self.path)

    def fail(self):
        super(Walking, self).fail()
        libtcod.path_delete(self.path)

    def __str__(self):
        return "Going somewhere"
