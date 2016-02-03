from tests import TavernTest
from tavern.events.events import STATUS_EVENT
from tavern.people.characters import Patron
from tavern.people.needs import Needs
from tavern.world.objects.functions import Functions
from tavern.world.objects.defaults import chair
from tavern.world.commands import AttendToCommand, OrderCommand, CreatureExit
from tavern.world.commands import BuyCommand, ReserveCommand


class TestAttendTo(TavernTest):
    def attend_to_counter(self, stop=False):
        # Attending below the counter at 9,11
        counter_attending_pos = (TavernTest.COUNTER_X,
                                 TavernTest.COUNTER_Y + 1,
                                 0)
        self.call_command(AttendToCommand(Functions.ORDERING,
                                          counter_attending_pos,
                                          stop))

    def test_start_attending(self):
        """The AttendToCommand should open up services."""
        self.assertEqual(
            len(self.tavern_map.available_services[Functions.ORDERING]),
            0,
            'There should not be attended services in the new tavern.'
        )
        self.attend_to_counter()
        self.assertEqual(
            len(self.tavern_map.available_services[Functions.ORDERING]),
            1,
            'There should be one attended services in the tavern after'
            ' a call to AttendToCommand.'
        )

    def test_stop_attending(self):
        """Calling the AttendToCommand with the stop flag should reverse
        the effect and stop the attendance."""
        self.attend_to_counter()
        self.attend_to_counter(stop=True)
        self.assertEqual(
            len(self.tavern_map.available_services[Functions.ORDERING]),
            0,
            'There should be not be an available service anymore after a '
            'call to AttendToCommand.'
        )

    def test_attending_opening_proper_slots(self):
        """AttendTo being used for serviceable objects, it takes a
        position and then open services for each objects around,
        in the tile opposite to the original position, across the object
        """
        self.attend_to_counter()
        available = self.tavern_map.available_services[Functions.ORDERING]
        tested_destination = (TavernTest.COUNTER_X, TavernTest.COUNTER_Y - 1,
                              0)
        self.assertEqual(tested_destination, available[0],
                         'AttendingTo did not open the proper coords.')


class TestOrder(TavernTest):
    def get_patron(self):
        needs = Needs(1, 0, 0, 0)
        return Patron(0, 0, 1, 'Name', 20, needs)

    def test_failing_order(self):
        """A failure to meet a customer order should send the drinks
        trouble flag."""
        patron = self.get_patron()
        drink_stock = self.tavern.store.amount_of(self.world.goods.drinks[0])
        self.assertEqual(0, drink_stock)
        self.call_command(OrderCommand(patron))
        self.assertReceived(STATUS_EVENT,
                            {'status': 'drinks', 'flag': False})
        self.assertFalse(patron.has_a_drink)

    def test_successful_order(self):
        """A successful order should reduce cash, storage and
        put the flag "has a drink" on patron."""
        basic_drink = self.world.goods.drinks[0]
        self.tavern.store.add(basic_drink, 1)
        patron = self.get_patron()
        self.call_command(OrderCommand(patron))
        self.assertReceived(STATUS_EVENT,
                            {'status': 'drinks', 'flag': True})
        self.assertTrue(patron.has_a_drink)
        self.assertEqual(patron.money, 20 - basic_drink.selling_price)
        self.assertEqual(self.tavern.store.amount_of(basic_drink), 0)


class TestCreatureExit(TavernTest):
    def test_leaving_tavern(self):
        """A CreatureExit command should remove the creature in
        the command from the list of creatures currently here."""
        self.customers.make_customer()
        patron = self.tavern.creatures[1]
        self.call_command(CreatureExit(patron))
        self.assertNotIn(patron, self.tavern.creatures)


class TestBuy(TavernTest):
    def make_transaction(self, cancel=False):
        self.call_command(BuyCommand(self.world.goods.drinks[0], 1, cancel))

    def test_buy(self):
        """Buying something should add it in the store and
        remove its cost from cash."""
        cash_at_fist = self.tavern.cash
        self.make_transaction()
        self.assertEqual(
            self.tavern.store.amount_of(self.world.goods.drinks[0]),
            1, 'Buying did not update stocks.')
        self.assertEqual(
            self.tavern.cash,
            cash_at_fist - self.world.goods.drinks[0].buying_price,
            'Buying did not update cash.')

    def test_cancel(self):
        """Canceling a buy should remove buying goods from the
        store and reimburse the cost money."""
        cash_at_first = self.tavern.cash
        self.make_transaction()
        self.make_transaction(True)
        self.assertEqual(
            self.tavern.store.amount_of(self.world.goods.drinks[0]), 0)
        self.assertEqual(self.tavern.cash, cash_at_first)


class TestReserveSeat(TavernTest):
    CHAIR_X = 9
    CHAIR_Y = 6

    def test_reserve(self):
        """Reserving a seat should remove it from the available services."""
        # There must be an existing service first
        self.chair_pos = (self.CHAIR_X, self.CHAIR_Y, 0)
        self.add_object(chair, self.CHAIR_X, self.CHAIR_Y)
        seatings = self.tavern_map.used_services[Functions.SITTING]
        self.assertNotIn(self.chair_pos, seatings)
        self.call_command(ReserveCommand(self.chair_pos, Functions.SITTING))
        self.assertIn(self.chair_pos, seatings)

    def test_cancel_reservation(self):
        """Canceling a seat reservation should put it pack amongst
        available services."""
        self.chair_pos = (self.CHAIR_X, self.CHAIR_Y, 0)
        # There must be an existing service first
        self.add_object(chair, self.CHAIR_X, self.CHAIR_Y)
        # Reserve it then unreseve it
        self.call_command(ReserveCommand(self.chair_pos, Functions.SITTING))
        self.call_command(
            ReserveCommand(self.chair_pos, Functions.SITTING, True))
        busy_seatings = self.tavern_map.used_services[Functions.SITTING]
        self.assertNotIn((self.chair_pos), busy_seatings)
        free_seatings = self.tavern_map.available_services[Functions.SITTING]
        self.assertIn((self.chair_pos), free_seatings)
