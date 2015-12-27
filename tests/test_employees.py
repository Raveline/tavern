from tests import TavernTest
from tavern.people.tasks.tasks_employees import (
    Serving, TakeOrder, FollowRecipe, FollowProcess, HaveSomethingDelivered,
    DeliverTask
)


class TestEmployees(TavernTest):

    def base_conditions(self):
        """
        Build a patron that is thirsty and hungry.
        """
        patron = self._build_thirsty_customer()
        patron.needs.hunger = 1
        self.add_drinks()
        self.add_chair()
        return patron

    def test_publican_go_to_counter(self):
        """If there is no other task, and a counter is there,
        the Publican will go there."""
        # By defaut, our tavern is created with a publican
        publican = self.tavern.creatures[0]
        self.assertCanTickTillTaskIs(publican, Serving, 20)

    def test_employee_will_go_pick_order(self):
        """A free employee with an order to pick should go and pick it up."""
        employee = self._make_employee()
        self.base_conditions()
        self.assertCanTickTillTaskIs(employee, TakeOrder, 100)

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
        # And kitchen ingredients in storage !
        self.add_ingredients()

        def employee_is_preparing_food():
            return isinstance(employee.current_activity, FollowRecipe)

        def employee_is_cutting_food():
            return isinstance(employee.current_activity, FollowProcess)

        def employee_is_creating_meal():
            return isinstance(employee.current_activity, HaveSomethingDelivered)

        def employee_is_delivering():
            return isinstance(employee.current_activity, DeliverTask)

        self.assertCanTickTillTaskIs(employee, FollowRecipe, 100)
        self.assertCanTickTillTaskIs(employee, FollowProcess, 80)
        self.assertCanTickTillTaskIs(employee, HaveSomethingDelivered, 80)
        self.assertCanTickTillTaskIs(employee, DeliverTask, 200)
