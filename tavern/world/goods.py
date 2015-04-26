class GoodsType:
    CLASSIC_DRINKS = 0
    FANCY_DRINKS = 1
    FOOD = 2

goods_type_to_store_cell_cost = {
    GoodsType.CLASSIC_DRINKS: .01,
    GoodsType.FANCY_DRINKS: .01,
    GoodsType.FOOD: .1
}


class Goods:
    def __init__(self, name, goods_type, buying_price, selling_price):
        self.name = name
        self.goods_type = goods_type
        self.buying_price = buying_price
        self.selling_price = selling_price
        self.store_cell_cost = goods_type_to_store_cell_cost(self.goods_type)

    def __str__(self):
        return self.name

DRINKS = [Goods('Ale', GoodsType.CLASSIC_DRINKS, 10, 12),
          Goods('Wine', GoodsType.FANCY_DRINKS, 15, 20),
          Goods('Spirits', GoodsType.CLASSIC_DRINKS, 10, 13)]
