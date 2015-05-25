from tests import TavernTest
from tavern.people.tasks.tasks_employees import (
    Serving, TakeOrder, PrepareFood, CutFood, CookFood, CreateMeal,
    DeliverTask
)


class TestEmployees(TavernTest):
    def test_publican_go_to_counter(self):
        """If there is no other task, and a counter is there,
        the Publican will go there."""
        # By defaut, our tavern is created with a publican
        publican = self.tavern.creatures[0]

        def publican_is_serving():
            return isinstance(publican.current_activity, Serving)

        self.assertCanTickTill(publican_is_serving, 20)

    def base_conditions(self):
        patron = self._build_thirsty_customer()
        patron.needs.hunger = 1
        self.add_drinks()
        self.add_chair()
        return patron

    def test_employee_will_go_pick_order(self):
        """A free employee with an order to pick should go and pick it up."""
        employee = self._make_employee()
        self.base_conditions()

        def assert_is_taking_order():
            return isinstance(employee.current_activity, TakeOrder)

        self.assertCanTickTill(assert_is_taking_order, 100)

    def test_failed_order(self):
        """If an order has been passed, but is not satisfied,
        after a while, the customer will leave."""
        self._make_employee()
        patron = self.base_conditions()

        def patron_has_left():
            return patron not in self.tavern.creatures

        self.assertCanTickTill(patron_has_left, 500)

    def test_cook_order(self):
        """If a hungry patron has ordered food, employees should
        go, prepare it."""
        employee = self._make_employee()
        self.base_conditions()
        # We need the kitchen for the test to work
        self.add_kitchen()

        def employee_is_preparing_food():
            return isinstance(employee.current_activity, PrepareFood)

        def employee_is_cutting_food():
            return isinstance(employee.current_activity, CutFood)

        def employee_is_cooking_food():
            return isinstance(employee.current_activity, CookFood)

        def employee_is_creating_meal():
            return isinstance(employee.current_activity, CreateMeal)

        def employee_is_delivering():
            return isinstance(employee.current_activity, DeliverTask)

        self.assertCanTickTill(employee_is_preparing_food, 100)
        self.assertCanTickTill(employee_is_cutting_food, 80)
        self.assertCanTickTill(employee_is_cooking_food, 80)
        self.assertCanTickTill(employee_is_creating_meal, 20)
        self.assertCanTickTill(employee_is_delivering, 100)
