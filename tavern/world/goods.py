from tavern.world.objects.functions import Functions
import tavern.world.colors as Colors


class GoodsType:
    CLASSIC_DRINKS = 0
    FANCY_DRINKS = 1
    FOOD = 2
    VEGETABLES = 3
    MEAT = 4

goods_type_to_store_cell_cost = {
    GoodsType.CLASSIC_DRINKS: .01,
    GoodsType.FANCY_DRINKS: .01,
    GoodsType.FOOD: .1,
    GoodsType.VEGETABLES: .1,
    GoodsType.MEAT: .1
}


class Processing(object):
    """The general notion of having to handle one or several GOODS,
    at a particular object having a FUNCTION for a given TIME."""
    def __init__(self, goods_and_quantity, function, time, name):
        # A list of pair (goods, quantity)
        self.goods_and_quantity = goods_and_quantity
        self.function = function
        self.time = time
        self.name = name


class Recipe(object):
    """The process or multi-process that is needed to
    build one item."""
    def __init__(self, processes, output):
        self.processes = processes
        self.output = output

    def is_recipe_possible(self, store):
        """Given the available things in store. Will NOT check if the
        services needed are available in the tavern."""
        for p in self.processes:
            goods, amount = p.goods_and_quantity
        return True


class Goods(object):
    def __init__(self, name, goods_type, buying_price, selling_price,
                 character, color, quality=1):
        self.name = name
        self.goods_type = goods_type
        self.buying_price = buying_price
        self.selling_price = selling_price
        self.store_cell_cost = goods_type_to_store_cell_cost[self.goods_type]
        self.character = character
        self.color = color
        self.block = False
        self.quality = quality

    def __str__(self):
        return self.name


# Goods
ale = Goods('Ale', GoodsType.CLASSIC_DRINKS, 10, 12, '.', Colors.ALE_AMBER)
wine = Goods('Wine', GoodsType.FANCY_DRINKS, 15, 20, '.', Colors.WINE_RED)
spirits = Goods('Spirits', GoodsType.CLASSIC_DRINKS, 10, 13, '.',
                Colors.SPIRITS_ABSINTH)
meat = Goods('Meat', GoodsType.MEAT, 4, 0, ';', Colors.MEAT_BLOOD)
vegetables = Goods('Vegetables', GoodsType.VEGETABLES, 1, 0, ':',
                   Colors.VEGETABLES_APPLE)
basic_meal = Goods('Basic Meal', GoodsType.FOOD, 6, 0, '^', Colors.MEAL_BUFF)


class GoodsList(object):
    """
    A class to list accessible goods and store them by type.
    """
    def __init__(self):
        self.drinks = [ale, wine, spirits]
        self.primary_materials = [meat, vegetables]
        self.food = [basic_meal]

    @property
    def supplies(self):
        return self.drinks + self.primary_materials

    @property
    def sellables(self):
        return self.drinks + self.food

# Process step
vegetable_preparation = Processing((vegetables, 1), Functions.WORKSHOP, 10,
                                   "Cutting ingredients")
meat_preparation = Processing((meat, 1), Functions.COOKING, 15, "Cooking meat")
meal_finish = Processing((), Functions.WORKSHOP, 1,
                         "Finishing to prepare a meal")

# Recipes
r_basic_meal = Recipe([vegetable_preparation, meat_preparation, meal_finish],
                      basic_meal)

recipes = {basic_meal: r_basic_meal}


def sort_by_price(iterable):
    """
    Return a collection sorted by ascending prices
    """
    return sorted(iterable, key=lambda i: i.selling_price)


def sort_by_quality_and_price(iterable):
    """
    Return a collection sorted by descending quality and ascending prices
    """
    return sorted(iterable, key=lambda i: (i.quality, -i.selling_price),
                  reverse=True)
