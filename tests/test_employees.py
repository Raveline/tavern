from tests import TavernTest
from tavern.utils import bus
from tavern.people.tasks.tasks_employees import Serving, TakeOrder
from tavern.people.employees import TAVERN_WAITER


class TestEmployees(TavernTest):
    def test_publican_go_to_counter(self):
        """If there is no other task, and a counter is there,
        the Publican will go there."""
        # By defaut, our tavern is created with a publican
        publican = self.tavern.creatures[0]

        def publican_is_serving():
            return isinstance(publican.current_activity, Serving)

        self.assertCanTickTill(publican_is_serving, 20)

    def _make_employee(self):
        self.customers.make_customer()
        patron = self.tavern.creatures[1]
        bus.bus.publish({'recruit': patron,
                         'profile': TAVERN_WAITER}, bus.CUSTOMER_EVENT)
        return self.tavern.creatures[1]

    def test_employee_will_go_pick_order(self):
        """A free employee with an order to pick should go and pick it up."""
        employee = self._make_employee()
        # This one also wants to eat !
        patron = self._build_thirsty_customer()
        patron.needs.hunger = 1
        self.add_drinks()
        self.add_chair()

        def assert_is_taking_order():
            return isinstance(employee.current_activity, TakeOrder)

        self.assertCanTickTill(assert_is_taking_order, 100)
