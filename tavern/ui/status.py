import libtcodpy as tcod


class StatusFlags:
    NO_BASICS_DRINKS = 'D'
    NO_FANCY_DRINKS = 'Q'
    NO_SERVICE = 'S'


class Status(object):
    def __init__(self):
        self.current_state = ''
        self.money = 0
        self.flags = []
        self.pause = False

    def receive(self, event):
        event_data = event.get('data')
        if event_data.get('status') == 'drinks':
            if event_data.get('flag'):
                self.remove_flag(StatusFlags.NO_BASICS_DRINKS)
            else:
                self.add_flag(StatusFlags.NO_BASICS_DRINKS)

    def add_flag(self, flag):
        if flag not in self.flags:
            self.flags.append(flag)

    def remove_flag(self, flag):
        if flag in self.flags:
            self.flags.remove(flag)

    def __repr__(self):
        return "Status bar"
