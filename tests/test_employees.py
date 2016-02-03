from tests import TavernTest
from tavern.people.tasks.employee import (
    Serving, TakeOrder, FollowProcess, HaveSomethingDelivered,
    DeliverTask
)
from tavern.people.employees import TAVERN_COOK, TAVERN_WAITER


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
        waiter = self._make_employee(TAVERN_WAITER)
        cook = self._make_employee(TAVERN_COOK)

        self.base_conditions()
        # We need the kitchen for the test to work
        self.add_kitchen()
        # And kitchen ingredients in storage !
        self.add_ingredients()

        self.assertCanTickTillTaskIs(cook, FollowProcess, 280)
        self.assertCanTickTillTaskIs(cook, HaveSomethingDelivered, 80)
        self.assertCanTickTillTaskIs(waiter, DeliverTask, 200)
