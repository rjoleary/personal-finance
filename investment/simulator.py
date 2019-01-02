from decimal import Decimal
from investment.account import PseudoAccount
from investment.time import Month


class Event(object):
    def apply(self, accounts):
        raise NotImplementedError('Override in sub class')


class Transfer(Event):
    def __init__(self, from_account, to_account, amount):
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount

    def apply(self, accounts, date):
        accounts[self.from_account].add(-self.amount, date)
        accounts[self.to_account].add(self.amount, date)


class Interest(Event):
    def __init__(self, monthly, account):
        self.monthly = monthly
        self.account = account

    def apply(self, accounts, date):
        accounts[self.account].add(accounts[self.account].value * self.monthly, date)


def net_worth(accounts):
    # TODO: currency conversion
    total = Decimal()
    for account in accounts.values():
        total += account.worth
    return total


# Note: real rate of return takes fees and inflation into account

def simulate(start, end, events, accounts, print_accounts=[]):
    print('year,' + ','.join(print_accounts))

    date = start
    while date != end:
        for event in events:
            event.apply(accounts, date)

        if date.month == 1:
            print(str(date.year) + ',' + ','.join(str(accounts[name]) for name in print_accounts))

        date = date.succ()
