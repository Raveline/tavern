from collections import defaultdict

INPUT_EVENT = 0
AREA_SELECT = 1
PLAYER_ACTION = 2
FEEDBACK_EVENT = 3
GAME_EVENT = 4
WORLD_EVENT = 5
NEW_STATE = 6
PREVIOUS_STATE = 7
MENU_EVENT = 8
MENU_MODEL_EVENT = 9
CUSTOMER_EVENT = 10

EVENTS_NAMES = ['Input event', 'Area select', 'Player action', 'Feedback event',
                'Game event', 'World event', 'New state', 'Previous state',
                'Menu event', 'Menu model event', 'Customer event']


class Bus(object):
    def __init__(self):
        self.events = defaultdict(list)

    def subscribe(self, receiver, event_type):
        self.events[event_type].append(receiver)

    def unsubscribe(self, receiver, event_type):
        try:
            self.events.get(event_type).remove(receiver)
        except Exception as a:
            print(str(a))
            self.publish("Trying to remove a receiver that was not subscribed")

    def publish(self, event, event_type=FEEDBACK_EVENT):
        event = {'type': event_type,
                 'data': event}
        self.display_event(event)
        # For event type, act like a stack
        if event_type == MENU_EVENT:
            self.events.get(event_type)[-1].receive(event.get('data'))
        # In any other case, publish for every listener
        else:
            for receiver in self.events.get(event_type):
                receiver.receive(event)

    def display_event(self, event):
        print('Event fired. Type %s - data : %s'
              % (EVENTS_NAMES[event['type']], event['data']))

    def __str__(self):
        representation = []
        for idx, event_name in enumerate(EVENTS_NAMES):
            representation.append(event_name)
            for subscriber in self.events[idx]:
                representation.append('- %s' % repr(subscriber))
        return '\n'.join(representation)

# Beware, this is global
bus = Bus()
