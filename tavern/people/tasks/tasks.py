import libtcodpy as tcod
from random import choice, randint

from tavern.utils import bus


class ImpossibleTask(Exception):
    pass


class Task(object):
    def __init__(self, length=0):
        self.tick_time = 0
        self.length = length
        self.failed = False
        self.finished = False

    def tick(self, world_map, creature):
        self.tick_time += 1

    def check_length(self):
        if self.tick_time == self.length:
            self.finish()
            return True
        else:
            return False

    def call_command(self, command):
        bus.bus.publish({'command': command}, bus.WORLD_EVENT)

    def fail(self):
        self.failed = True

    def finish(self):
        self.finished = True


class Wandering(Task):
    """Fool around for 10 ticks."""
    def __init__(self, length=10):
        super(Wandering, self).__init__(length)

    def tick(self, world_map, creature):
        if not self.check_length():
            self.wander(world_map, creature)
        super(Wandering, self).tick(world_map, creature)

    def wander(self, world_map, creature):
        if randint(0, 2) == 0:
            pos = choice(world_map.get_legit_moves_from(creature.to_pos()))
            creature.move(pos)

    def __str__(self):
        return "Being idle"


class Walking(Task):
    def __init__(self, world_map, creature, pos):
        super(Walking, self).__init__()
        self.dest = pos
        self.path = None

    def compute_path(self, world_map, creature):
        if not creature.is_at_pos(self.dest):
            self.path = world_map.path_from_to(creature.to_pos(), self.dest)
            self.path_length = tcod.path_size(self.path)
            if self.path_length == 0:
                self.fail()
                raise ImpossibleTask('No path from %d, %d, %d to %d, %d, %d'
                                     % (creature.to_pos() + self.dest))
            # The tick time MUST be reset, in case we recompute path
            # during the task.
            self.tick_time = 0
        else:
            self.path = None
            self.path_length = 0
            self.finish()

    def tick(self, world_map, creature):
        if self.tick_time == 0:
            self.compute_path(world_map, creature)
        if self.tick_time < self.path_length:
            x, y = tcod.path_get(self.path, self.tick_time)
            z = creature.z
            if not world_map[(x, y, z)].is_walkable():
                # Path is not walkable anymore !
                # We'll try to rebuild it...
                self.compute_path(world_map, creature)
            else:
                creature.move((x, y, 0))
        else:
            self.finish()
        super(Walking, self).tick(world_map, creature)

    def finish(self):
        super(Walking, self).finish()
        self.free_path()

    def fail(self):
        super(Walking, self).fail()
        self.free_path()

    def free_path(self):
        if self.path:
            tcod.path_delete(self.path)
            self.path = None

    def __str__(self):
        return "Going somewhere"
