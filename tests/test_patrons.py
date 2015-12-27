from tests import TavernTest
from tavern.people.tasks.tasks_patron import (
    Ordering, Leaving, Drinking, Eating, TableOrder)
from tavern.world.objects.functions import Functions


class TestPatron(TavernTest):

    def test_go_to_counter(self):
        """A thirsty patron will go to the counter and try to order.
        If he cannot, he will leave."""
        patron = self._build_thirsty_customer()

        self.assertCanTickTillPatronTaskIs(patron, Ordering, 30)

        # Here, since we do not have drinks to give him, he should leave
        self.assertCanTickTillPatronTaskIs(patron, Leaving, 50)

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
        self.assertCanTickTillPatronTaskIs(patron, Drinking, 10)
        # Customer should still be in the list of tavern creatures
        self.assertIn(patron, self.tavern.creatures)
        # Wait for the customer to stop drinking and leave
        self.tick_for(100)
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
        self.assertCanTickTillPatronTaskIs(patron, TableOrder, 70)

        # Customer will then leave...
        self.assertCanTickTillPatronTaskIs(patron, Leaving, 200)

    def test_order_food_complete(self):
        """Customers should be able to order (and eat !) food."""
        # An employee to take care of orders
        self._make_employee()
        # We need the kitchen for the test to work
        self.add_kitchen()
        # This one also wants to eat !
        patron = self._build_thirsty_customer()
        patron.needs.hunger = 1
        self.add_drinks()
        self.add_chair()

        self.assertCanTickTillPatronTaskIs(patron, Eating, 300)
