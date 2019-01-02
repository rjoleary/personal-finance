from decimal import Decimal
from investment.time import Month


# TODO: should be immutable, maybe a namedtuple?
class Event(object):
    def apply(self, accounts):
        raise NotImplementedError('Override in sub class')


class Salary(Event):
    def __init__(self, monthly, deposit_into):
        self.monthly = monthly
        self.deposit_into = deposit_into

    def apply(self, accounts):
        accounts[self.deposit_into].value += self.monthly


class Interest(Event):
    def __init__(self, monthly, account):
        self.monthly = monthly
        self.account = account

    def apply(self, accounts):
        accounts[self.account].value *= self.monthly


def net_worth(accounts):
    total = Decimal()
    for account in accounts.values():
        total += account.value
    return total


# Note: real rate of return takes fees and inflation into account

def simulate(start, end, events, accounts):
    print('year,' + ','.join(account for account in accounts.keys()))

    cur = start
    while cur != end:
        for event in events:
            event.apply(accounts)

        if cur.month == 1:
            print(str(cur.year) + ',' + ','.join(str(a) for a in accounts.values()))

        cur = cur.succ()
