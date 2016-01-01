from tavern.world.tavern_map import TavernMap
from tavern.world.store import StorageSystem
from tavern.world.task_list import TaskList
from tavern.people.employees import make_recruit_out_of
from itertools import chain
from tavern.world.objects.objects import Rooms


class Tavern(object):
    """The abstract entity of a tavern, meaning its physical
    manifestation (the TavernMap), its financial situation (cash),
    its storage situation (StorageSystem) the people inside (creatures).
    """
    def __init__(self, width, height, cash=2000, tiles=None):
        self.tavern_map = TavernMap(width, height, tiles)
        # Storage
        self.store = StorageSystem()
        # Money
        self.cash = cash
        # Creatures
        self.creatures = []
        # Task list
        self.tasks = TaskList()

    def add_creature(self, creature):
        self.creatures.append(creature)

    def remove_creature(self, creature):
        self.creatures.remove(creature)

    def handle_customer_event(self, event_data):
        if event_data.get('customer'):
            self.creatures.append(event_data.get('customer'))
        elif event_data.get('recruit'):
            recruit = event_data.get('recruit')
            # First, we remove our recruit from the existing creature list...
            self.creatures.remove(recruit)
            # Then we rebuild it, anew !
            new_creature = make_recruit_out_of(recruit,
                                               event_data.get('profile'))
            # ... and we add it back to the list of creatures !
            self.creatures.append(new_creature)

    def creature_at(self, x, y, z):
        cre = [c for c in self.creatures
               if c.x == x and c.y == y and c.z == z]
        if cre:
            return cre[0]

    def redispatch_store(self):
        """
        Storage is not, like in other kind of games (city builders like,
        Dwarf Fortress, etc.) really a place where thing is stored. When
        an employee need something from storage, he "magically" gets it.
        But we need to recompute the way it is displayed each time storage
        change so that it is properly shown to the player.
        """
        all_storage_tiles = list(chain(*self.tavern_map.rooms[Rooms.STORAGE]))
        all_storage_cells = self.store.cell_representation
        number_of_cells = len(all_storage_cells)
        for idx, tile in enumerate(all_storage_tiles):
            if idx < number_of_cells:
                self.tavern_map[tile].tile_object = all_storage_cells[idx]
            else:
                self.tavern_map[tile].tile_object = None
