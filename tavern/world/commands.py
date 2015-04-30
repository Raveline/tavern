class Command(object):
    """A simple implementation of Command pattern.
    """
    def execute(self, obj):
        pass


class BuyCommand(object):
    def __init__(self, goods, quantity, cancel=False):
        self.goods = goods
        self.quantity = quantity
        self.money_value = goods.buying_price
        self.cancel = cancel

    def execute(self, world):
        if not self.cancel:
            self.world.cash += self.money_value
            self.world.store.add(self.goods, self.quantity)
        else:
            # Cancel a buy
            self.world.cash -= self.money_value
            self.world.store.take(self.goods, self.quantity)