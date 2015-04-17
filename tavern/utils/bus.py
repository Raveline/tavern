from collections import defaultdict

INPUT_EVENT = 0
AREA_SELECT = 1
PLAYER_ACTION = 2
FEEDBACK_EVENT = 3
GAME_EVENT = 4
WORLD_EVENT = 5
NEW_STATE = 6
PREVIOUS_STATE = 7

EVENTS_NAMES = ['Input event', 'Player action', 'Feedback event', 'Game event',
                'State event']


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
        for receiver in self.events.get(event_type):
            receiver.receive(event)

    def __str__(self):
        representation = []
        for idx, event_name in enumerate(EVENTS_NAMES):
            representation.append(event_name)
            for subscriber in self.events[idx]:
                representation.append('- %s' % repr(subscriber))
        return '\n'.join(representation)

# Beware, this is global
bus = Bus()
