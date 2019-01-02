from decimal import Decimal
from investment.moneyfmt import moneyfmt

class Account(object):
    def __init__(self, value=Decimal(), currency='USD'):
        self.value = value
        self.currency = currency

    def __str__(self):
        return '%s%s' % (moneyfmt(self.value), self.currency)
