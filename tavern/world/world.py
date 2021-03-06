from tavern.events.events import CUSTOMER_EVENT
from groggy.events import bus


class World(object):
    '''
    The world where the game takes place.
    It should features:
        - geographic area and events.
        - the tavern itself (of course !)
        - the "inventions" linked to this world, such as beers and objects
          created by the player, and also all existing jobs (things the player
          should not be able to modify, but that "belongs" to the very idea
          of context associated to the world).
    '''

    def __init__(self, tavern, goods, jobs):
        self.tavern = tavern
        self.goods = goods
        self.jobs = jobs

    def tick(self):
        for crea in self.tavern.creatures:
            crea.tick(self)

    def receive(self, event):
        event_data = event.get('data')
        if event.get('type') == CUSTOMER_EVENT:
            self.tavern.handle_customer_event(event_data)
        elif event.get('type') == bus.WORLD_EVENT:
            command = event_data.get('command')
            if command:
                command.execute(self)

    # For now, we will redefine common Tavern
    # accessors as property of the world to
    # avoid long accesses
    @property
    def tavern_map(self):
        return self.tavern.tavern_map

    @property
    def store(self):
        return self.tavern.store

    @property
    def tasks(self):
        return self.tavern.tasks

    @property
    def cash(self):
        return self.tavern.cash
