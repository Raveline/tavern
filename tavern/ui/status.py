from tavern.events.events import STATUS_EVENT, MONEY_EVENT


class StatusFlags:
    NO_BASICS_DRINKS = 'D'
    NO_FANCY_DRINKS = 'Q'
    NO_SERVICE = 'S'


class Status(object):
    FRAMES_OF_DISPLAY = 100
    def __init__(self):
        self.current_state = ''
        self.money = 0
        self.flags = []
        self.pause = False
        self.last_money_movement = None
        self.delta_display = 0

    def receive(self, event):
        event_data = event.get('data')
        event_type = event.get('type')
        if event_type == STATUS_EVENT:
            if event_data.get('status') == 'drinks':
                if event_data.get('flag'):
                    self.remove_flag(StatusFlags.NO_BASICS_DRINKS)
                else:
                    self.add_flag(StatusFlags.NO_BASICS_DRINKS)
        elif event_type == MONEY_EVENT:
            self.last_money_movement = event_data.get('amount')
            self.delta_display = 0

    def add_flag(self, flag):
        if flag not in self.flags:
            self.flags.append(flag)

    def remove_flag(self, flag):
        if flag in self.flags:
            self.flags.remove(flag)

    def __repr__(self):
        return "Status bar"

    def delta_increment(self):
        self.delta_display += 1
        if self.delta_display > self.FRAMES_OF_DISPLAY:
            self.delta_display = 0
            self.last_money_movement = None
