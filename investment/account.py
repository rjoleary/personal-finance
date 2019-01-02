from collections import namedtuple
from decimal import Decimal
from investment.moneyfmt import moneyfmt

LedgerEntry = namedtuple('LedgerEntry', ['value', 'date'])

class Account(object):
    def __init__(self, value=Decimal(), currency='USD'):
        self._value = value
        self.currency = currency
        self.ledger = []

    def __str__(self):
        return '%s%s' % (moneyfmt(self._value), self.currency)

    @property
    def value(self):
        return self._value

    @property
    def worth(self):
        # TODO: currency conversions
        return self.value

    def add(self, value, date):
        self.ledger.append(LedgerEntry(value, date))
        self._value += value

    def ytd(self, date):
        value = Decimal()
        for entry in self.ledger:
            if entry.date.year == date.year:
                value += entry.value
        return value


class PseudoAccount(Account):
    """Pseudo-accounts are for accounting and do not contribute to net worth.

    For example, withheld taxes.
    """
    @property
    def worth(self):
        return Decimal()
