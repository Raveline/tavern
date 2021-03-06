from operator import itemgetter


class Needs(object):
    THIRST = 0
    HUNGER = 1
    GAMBLE = 2
    SLEEP = 3

    def __init__(self, thirst, hunger, gamble, sleep):
        self.thirst = thirst
        self.hunger = hunger
        self.gamble = gamble
        self.sleep = sleep

    def as_dict(self):
        return {Needs.THIRST: self.thirst,
                Needs.HUNGER: self.hunger,
                Needs.GAMBLE: self.gamble,
                Needs.SLEEP: self.sleep}

    def sum_needs(self):
        return self.thirst + self.hunger + self.gamble + self.sleep

    def has_needs(self):
        return self.thirst > 0 or self.hunger > 0 or self.gamble > 0\
            or self.sleep > 0

    def get_priority_needs(self):
        """
        Returns the type of the highest need.

        >>> n = Needs(1, 1, 1, 3)
        >>> n.get_priority_needs() == Needs.SLEEP
        True
        >>> n2 = Needs(3, 1, 0, 2)
        >>> n2.get_priority_needs() == Needs.THIRST
        True
        """
        return max(self.as_dict().items(), key=itemgetter(1))[0]

    def cancel_needs(self):
        self.thirst = 0
        self.hunger = 0
        self.gamble = 0
        self.sleep = 0
