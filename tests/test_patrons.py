from tests import TavernTest
from tavern.people.tasks.patron import (
    Ordering, Leaving, Drinking, Eating, TableOrder)
from tavern.world.objects.functions import Functions
from tavern.people.employees import TAVERN_COOK, TAVERN_WAITER


class TestPatron(TavernTest):

    def test_go_to_counter(self):
        """A thirsty patron will go to the counter and try to order.
        If he cannot, he will leave."""
        patron = self._build_thirsty_customer()

        self.assertCanTickTillTaskIs(patron, Ordering, 30)

        # Here, since we do not have drinks to give him, he should leave
        self.assertCanTickTillTaskIs(patron, Leaving, 50)

    def test_order_sit_drink_leave(self):
        """Thirsty patrons will order a drink and, if they get one,
        go to a chair to drink it. They will then leave."""
        patron = self._build_thirsty_customer()
        # This time, we MUST have drinks.
        self.add_drinks()
        self.add_chair()

        num_available_chairs = len(
            self.tavern_map.available_services[Functions.SITTING]
        )

        def one_chair_is_reserved():
            return len(self.tavern_map.
                       available_services[Functions.SITTING])\
                == (num_available_chairs - 1)

        self.assertCanTickTill(one_chair_is_reserved, 30,
                               'No chair was reserved.')

        # Customer will then drink
        self.assertCanTickTillTaskIs(patron, Drinking, 10)
        # Customer should still be in the list of tavern creatures
        self.assertIn(patron, self.tavern.creatures)
        # Wait for the customer to stop drinking and leave
        self.assertCanTickTillTaskIs(patron, Leaving, 30)
        # Let one tick for the Leaving task to work...
        self.tick_for()
        # Customer should not be in the list of tavern creatures
        self.assertNotIn(patron, self.tavern.creatures)

    def test_order_food_no_waiter(self):
        """Customers leave if there is nobody to take their food order."""
        patron = self._build_thirsty_customer()
        # This one also wants to eat !
        patron.needs.hunger = 1
        self.add_drinks()
        self.add_chair()

        # Customer will be waiting for someone to take his/her order.
        self.assertCanTickTillTaskIs(patron, TableOrder, 70)

        # Customer will then leave...
        # (After a wait determined by the task + the time required
        # to move from the chair to the exit...)
        self.assertCanTickTillTaskIs(patron, Leaving,
                                     TableOrder.ORDER_WAITING + 100)

    def test_order_food_complete(self):
        """Customers should be able to order (and eat !) food."""
        # An employee to take care of orders
        self._make_employee(TAVERN_WAITER)
        self._make_employee(TAVERN_COOK)
        # We need the kitchen for the test to work
        self.add_kitchen()
        self.add_ingredients()
        # This one also wants to eat !
        patron = self._build_thirsty_customer()
        patron.needs.hunger = 1
        self.add_drinks()
        self.add_chair()

        self.assertCanTickTillTaskIs(patron, Eating, 300)

    def test_multiple_customers(self):
        """See if there is no crash on a 5,000 tick-long crowded,
        equipped tavern."""
        self._make_employee()
        self.add_chair()
        self.add_kitchen()
        self.add_ingredients()
        self.add_drinks()
        for n in range(0, 30):
            self._build_thirsty_customer()
        self.tick_for(15000)
