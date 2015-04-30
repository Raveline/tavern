class Command(object):
    """A simple implementation of Command pattern.
    """
    def execute(self, obj):
        pass


class BuyCommand(object):
    def __init__(self, goods, quantity, cancel=False):
        self.goods = goods
        self.quantity = abs(quantity)
        self.money_value = goods.buying_price
        self.cancel = cancel

    def execute(self, world):
        if not self.cancel:
            # Do the buy
            world.cash -= self.money_value
            world.store.add(self.goods, self.quantity)
        else:
            # Cancel a buy
            world.cash += self.money_value
            world.store.take(self.goods, self.quantity)
