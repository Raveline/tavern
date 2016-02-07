class Ledger(object):
    """
    A simple ledger that will keep in memory everything that has been bought
    and sold.
    """
    def __init__(self):
        self.income = []
        self.expenses = []

    def receive(self, event_data):
        amount = event_data.get('amount', 0)
        label = event_data.get('label')
        if amount < 0:
            self.add_expense(amount, label)
        elif amount > 0:
            self.add_income(amount, label)

    def add_expense(self, amount, label):
        self.income.append((amount, label))

    def add_income(self, amount, label):
        self.expenses.append((amount, label))
