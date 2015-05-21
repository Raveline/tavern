from tests import TavernTest
from tavern.people.tasks import Ordering, Leaving, Drinking, TableOrder
from tavern.world.objects.functions import Functions
from tavern.world.goods import DRINKS
from tavern.world.actions import chair


class TestPatron(TavernTest):
    def _build_thirsty_customer(self):
        self.customers.make_customer()
        patron = self.tavern.creatures[-1]
        # This fellow will want to drink, and only drink
        patron.needs.thirst = 1
        patron.needs.hunger = 0
        patron.needs.gamble = 0
        patron.needs.sleep = 0
        # Money is not an issue
        patron.money = 1000
        return patron

    def add_drinks(self):
        self.tavern.store.add(DRINKS[0], 10)

    def test_go_to_counter(self):
        """A thirsty patron will go to the counter and try to order.
        If he cannot, he will leave."""
        patron = self._build_thirsty_customer()

        def is_ordering():
            return isinstance(patron.current_activity, Ordering)

        self.assertCanTickTill(is_ordering, 30)

        def is_leaving():
            return isinstance(patron.current_activity, Leaving)

        # Here, since we do not have drinks to give him, he should leave
        self.assertCanTickTill(is_leaving, 50)

    def test_order_sit_drink_leave(self):
        """Thirsty patrons will order a drink and, if they get one,
        go to a chair to drink it. They will then leave."""
        patron = self._build_thirsty_customer()
        # This time, we MUST have drinks.
        self.add_drinks()
        self.add_object(chair, 9, 6)
        num_available_chairs = len(
            self.tavern_map.available_services[Functions.SITTING]
        )

        def one_chair_is_reserved():
            return len(self.tavern_map.
                       available_services[Functions.SITTING])\
                == (num_available_chairs - 1)

        self.assertCanTickTill(one_chair_is_reserved, 30,
                               'No chair was reserved.')

        def customer_is_drinking():
            return isinstance(patron.current_activity, Drinking)

        # Customer will then drink
        self.assertCanTickTill(customer_is_drinking, 10)
        # Customer should still be in the list of tavern creatures
        self.assertIn(patron, self.tavern.creatures)
        # Wait for the customer to stop drinking and leave
        self.tick_for(100)
        # Customer should not be in the list of tavern creatures
        self.assertNotIn(patron, self.tavern.creatures)

    def test_order_food_no_waiter(self):
        """Customers might want to order food when there is no employee
        available for waiting. They should leave after a while."""
        patron = self._build_thirsty_customer()
        # This one also wants to eat !
        patron.needs.hunger = 1
        self.add_drinks()
        self.add_object(chair, 9, 6)

        def customer_want_to_order_something_to_eat():
            return isinstance(patron.current_activity, TableOrder)

        # Customer will be waiting for someone to take his/her order.
        self.assertCanTickTill(customer_want_to_order_something_to_eat, 70)
