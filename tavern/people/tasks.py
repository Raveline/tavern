import libtcodpy as libtcod
import random


class Task(object):
    def __init__(self):
        self.tick_time = 0
        self.finished = False

    def tick(self, world_map, creature):
        self.tick_time += 1


class Wandering(Task):
    def tick(self, world_map, creature):
        if self.tick_time <= 10:
            self.wander(world_map, creature)
            self.tick_time = 0
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


class Walking(Task):
    def __init__(self, world_map, creature, x, y):
        super(Walking, self).__init__()
        self.path = world_map.path_from_to(creature.x, creature.y, x, y)
        self.path_length = libtcod.path_size(self.path)

    def tick(self, world_map, creature):
        if self.tick_time < self.path_length:
            x, y = libtcod.path_get(self.path, self.tick_time)
            if not world_map.tiles[y][x].is_walkable():
                # Path is not walkable anymore !
                self.end_path()
            else:
                creature.move(x, y, 0)
        else:
            self.end_path()
        super(Walking, self).tick(world_map, creature)

    def end_path(self):
        libtcod.path_delete(self.path)
        self.finished = True

    def __str__(self):
        return "Going somewhere"
