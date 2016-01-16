from collections import defaultdict
from tavern.world.objects.functions import Functions
import tavern.world.colors as Colors


class GoodsType:
    CLASSIC_DRINKS = 0
    FANCY_DRINKS = 1
    FOOD = 2
    VEGETABLES = 3
    MEAT = 4
    GRAINS = 5
    AROMA = 6

goods_type_to_store_cell_cost = {
    GoodsType.CLASSIC_DRINKS: .01,
    GoodsType.FANCY_DRINKS: .01,
    GoodsType.FOOD: .1,
    GoodsType.VEGETABLES: .1,
    GoodsType.MEAT: .1,
    GoodsType.GRAINS: .01,
    GoodsType.AROMA: .01
}


class Processing(object):
    """The general notion of having to handle one or several GOODS,
    at a particular object having a FUNCTION for a given TIME."""
    def __init__(self, goods_and_quantities, function, time, name):
        # A list of pair (goods, quantity)
        self.goods_and_quantities = goods_and_quantities
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
        self.blocks = False
        self.quality = quality

    def __str__(self):
        return self.name


wine = Goods('Wine', GoodsType.FANCY_DRINKS, 15, 20, 'O', Colors.WINE_RED)
spirits = Goods('Spirits', GoodsType.CLASSIC_DRINKS, 10, 13, 'O',
                Colors.SPIRITS_ABSINTH)
meat = Goods('Meat', GoodsType.MEAT, 4, 0, ';', Colors.MEAT_BLOOD)
vegetables = Goods('Vegetables', GoodsType.VEGETABLES, 1, 0, ':',
                   Colors.VEGETABLES_APPLE)
basic_meal = Goods('Basic Meal', GoodsType.FOOD, 6, 0, '^', Colors.MEAL_BUFF)

# Grains
malt = Goods('Malt', GoodsType.GRAINS, 2, 0, 'm', Colors.MALT_BROWN)

# Aromas
mint = Goods('Mint', GoodsType.AROMA, 1, 0, 'i', Colors.VEGETABLES_APPLE)
hop = Goods('Hop', GoodsType.AROMA, 2, 0, 'h', Colors.VEGETABLES_APPLE)
nuts = Goods('Nuts', GoodsType.AROMA, 1, 0, 'n', Colors.CHAIR_WALNUT_STAIN)
herbs = Goods('Herbs', GoodsType.AROMA, 1, 0, '.', Colors.VEGETABLES_APPLE)


# Process step
vegetable_preparation = Processing([(vegetables, 1)], Functions.WORKSHOP, 10,
                                   "Cutting ingredients")
meat_preparation = Processing([(meat, 1)], Functions.COOKING, 15, "Cooking meat")
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


def build_beer(grains, aromas, roasted, name):
    beerTasks = []
    processable_grains = [(g, 1) for g in grains]
    processable_aromas = [(a, 1) for a in aromas]
    all_processable = processable_grains + processable_aromas
    if roasted:
        p = Processing(processable_grains, Functions.COOKING,
                       100, "Roasting grains")
        beerTasks.append(p)
    vat = Processing(all_processable, Functions.BREWING,
                     len(all_processable) * 30, "Brewing")
    beerTasks.append(vat)
    selling_price = sum([ing.buying_price
                         for ing in aromas + grains]) + 2
    beer = Goods(name, GoodsType.CLASSIC_DRINKS,
                 0, selling_price, '0', Colors.ALE_AMBER)
    return beer, Recipe(beerTasks, beer)

# Goods
ale, ale_recipe = build_beer([malt], [hop], False, 'Ale')
ale.buying_price = 10
ale.selling_price = 12


class GoodsList(object):
    """
    A class to list accessible goods and store them by type.
    """

    def __init__(self):
        self.drinks = [ale, wine, spirits]
        self.primary_materials = [meat, vegetables]
        self.food = [basic_meal]
        self.grains = [malt]
        self.aromas = [hop, vegetables, mint, nuts, herbs]
        self.recipes = defaultdict(lambda: defaultdict(list))
        self.recipes[GoodsType.CLASSIC_DRINKS][ale] = ale_recipe

    def add_drink(self, drink, recipe):
        self.drinks.append(drink)
        self.recipes[GoodsType.CLASSIC_DRINKS][drink] = recipe

    @property
    def supplies(self):
        return self.drinks + self.primary_materials + self.grains + self.aromas

    @property
    def sellables(self):
        return self.drinks + self.food
