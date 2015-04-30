import math
from collections import defaultdict


class StorageException(Exception):
    pass


class StorageSystem(object):
    def __init__(self, initial_goods=None):
        self.cells = 0
        self.store = defaultdict(int)
        if initial_goods is None:
            initial_goods = {}
        self.store = defaultdict(int, initial_goods)

    def add_cells(self, quantity):
        self.cells += quantity

    def add(self, goods, quantity):
        """
        Add <quantity> of type <goods> in store.
        If there is not enough room, raise an exception.
        Control of room availability is left to the caller.
        """
        if quantity <= self.current_available_cells():
            self.store[goods] += quantity
        else:
            raise StorageException('Adding %d of %s was too much. '
                                   'Not enough room in storage.'
                                   % (quantity, str(goods)))

    def take(self, goods, quantity):
        """
        Take <quantity> of type <goods> in store.
        if there is not enough goods, raise an exception.
        Control of goods availability is left to the caller.
        """
        self.store[goods] -= quantity
        if self.store[goods] < 0:
            raise StorageException('Taking %d of %s was too much. '
                                   'Not enough wares in storage.'
                                   % (quantity, str(goods)))

    def amount_of(self, goods):
        """
        How much of <goods> to we have in store ?
        """
        return self.store[goods]

    def can_take(self, goods, quantity):
        """
        Can I take <quantity> of <goods> (i.e., do we store enough for this) ?
        """
        return self.amount_of(goods) >= quantity

    def has(self, goods):
        """
        Do we store (any quantity superior to 0) of required goods ?
        """
        return self.amount_of(goods) > 0

    def can_store(self, goods, quantity):
        """
        Can I store <quantity> amount of <goods> ?
        """
        return self.goods_quantity_to_cell(goods, quantity)\
            <= self.current_available_cells()

    def goods_quantity_to_cell(self, goods, amount):
        """
        Translate the <amount> of this brand of <goods> to
        cell occupancy.
        """
        return math.ceil(amount * goods.store_cell_cost)

    def cell_to_goods_quantity(self, cells, goods):
        """
        Translate the amount of <cells> to a quantity of
        <goods>.
        """
        return math.ceil(cells / goods.store_cell_cost)

    def current_occupied_cells(self):
        current_occupied_cells = 0
        for goods, amount in self.store.iteritems():
            occupancy = self.goods_quantity_to_cell(goods, amount)
            current_occupied_cells += occupancy
        return current_occupied_cells

    def current_available_cells(self):
        return self.cells - self.current_occupied_cells()
