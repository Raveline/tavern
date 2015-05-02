import libtcodpy as libtcod
import random

from tavern.utils import bus
from tavern.world.commands import AttendToCommand


class Task(object):
    def __init__(self):
        self.tick_time = 0
        self.failed = False
        self.finished = False

    def tick(self, world_map, creature):
        self.tick_time += 1


class Wandering(Task):
    def tick(self, world_map, creature):
        if self.tick_time <= 10:
            self.wander(world_map, creature)
        else:
            self.finished = True
        super(Wandering, self).tick(world_map, creature)

    def wander(self, world_map, creature):
        if random.randint(0, 2) == 0:
            x, y, z = random.choice(world_map.get_legit_moves_from(
                creature.x, creature.y, creature.z))
            creature.move(x, y, z)

    def __str__(self):
        return "Being idle"


class Serving(Task):
    """As in serving people."""
    def __init__(self, creature, nature):
        super(Serving, self).__init__()
        bus.bus.publish({'command': AttendToCommand(nature,
                                                    (creature.x, creature.y))},
                        bus.WORLD_EVENT)
        self.stop_command = AttendToCommand(nature,
                                            (creature.x, creature.y),
                                            True)

    def end_shift(self):
        bus.bus.publish({'command': self.stop_command}, bus.WORLD_EVENT)

    def __str__(self):
        return "Serving customers"


class Walking(Task):
    def __init__(self, world_map, creature, x, y):
        super(Walking, self).__init__()
        self.path = world_map.path_from_to(creature.x, creature.y, x, y)
        self.path_length = libtcod.path_size(self.path)
        if self.path_length == 0:
            self.failed = True

    def tick(self, world_map, creature):
        if self.tick_time < self.path_length:
            x, y = libtcod.path_get(self.path, self.tick_time)
            if not world_map.tiles[y][x].is_walkable():
                # Path is not walkable anymore !
                self.end_path()
                self.failed = True
            else:
                print("Moving to %d, %d" % (x, y))
                print("Tick time : %d - path length : %d" % (self.tick_time,
                                                             self.path_length))
                creature.move(x, y, 0)
        else:
            self.end_path()
        super(Walking, self).tick(world_map, creature)

    def end_path(self):
        libtcod.path_delete(self.path)
        self.finished = True

    def __str__(self):
        return "Going somewhere"
