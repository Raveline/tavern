from tests import TavernTest
from tavern.people.tasks import Ordering, Leaving


class TestPatron(TavernTest):
    def _build_one_customer(self):
        self.customers.make_customer()
        return self.tavern.creatures[1]

    def test_go_to_counter(self):
        """A thirsty patron will go to the counter and try to order.
        If he cannot, he will leave."""
        patron = self._build_one_customer()
        # This fellow will want to drink, and only drink
        patron.needs.thirst = 1
        patron.needs.hunger = 0
        patron.needs.gamble = 0
        patron.needs.sleep = 0
        # Money is not an issue
        patron.money = 1000

        def is_ordering():
            return isinstance(patron.current_activity, Ordering)

        self.assertCanTickTill(is_ordering, 30)

        def is_leaving():
            return isinstance(patron.current_activity, Leaving)

        # Here, since we do not have drinks to give him, he should leave
        self.assertCanTickTill(is_leaving, 50)
