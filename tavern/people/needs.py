class Needs(object):
    def __init__(self, thirst, hunger, gamble, sleep):
        self.thirst = thirst
        self.hunger = hunger
        self.gamble = gamble
        self.sleep = sleep

    def has_needs(self):
        return self.thirst > 0 and self.hunger > 0 and self.gamble > 0\
            and self.sleep > 0

    def cancel_needs(self):
        self.thirst = 0
        self.hunger = 0
        self.gamble = 0
        self.sleep = 0
