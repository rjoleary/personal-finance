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
        if date.day != 1:
            return
        accounts[self.from_account].add(-self.amount, date)
        accounts[self.to_account].add(self.amount, date)


class Interest(Event):
    def __init__(self, monthly, account):
        self.monthly = monthly
        self.account = account

    def apply(self, accounts, date):
        if date.day != 1:
            return
        accounts[self.account].add(accounts[self.account].value * self.monthly, date)


def net_worth(accounts):
    # TODO: currency conversion
    total = Decimal()
    for account in accounts.values():
        total += account.worth
    return total


# Note: real rate of return takes fees and inflation into account

def simulate(start, end, events, accounts):
    date = start
    while date != end:
        for event in events:
            event.apply(accounts, date)

        if date.month == 1 and date.day == 1:
            yield date

        date = date.succ()
