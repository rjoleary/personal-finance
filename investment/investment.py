#!python3

from decimal import *
from collections import namedtuple

_Month = namedtuple('Month', ['year', 'month'])


class Error(Exception):
    """Base class for exceptions in this module."""


class ParseMonthError(Error):
    pass


class Month(_Month):
    MONTHS = {
            1: 'JAN',
            2: 'FEB',
            3: 'MAR',
            4: 'APR',
            5: 'MAY',
            6: 'JUN',
            7: 'JUL',
            8: 'AUG',
            9: 'SEP',
            10: 'OCT',
            11: 'NOV',
            12: 'DEC',
    }

    def succ(self):
        if self.month == 12:
            return Month(self.year + 1, 1)
        return Month(self.year, self.month + 1)

    def pred(self):
        if self.month == 1:
            return Month(self.year - 1, 12)
        return Month(self.year, self.month - 1)

    def __str__(self):
        return "%s%s" % (self.year, self.MONTHS.get(self.month, "ERR"))

    @classmethod
    def parse(cls, text):
        if len(text) != 7:
            raise ParseMonthError("Month must be 7 characters MMMYYYY")
        month = text[:3]
        year = text[3:]
        for k, v in cls.MONTHS.items():
            if v == month:
                return Month(int(year), k)

class Account(object):
    def __init__(self, value=Decimal(), currency='USD'):
        self.value = value
        self.currency = currency

    def __str__(self):
        return '%s%s' % (moneyfmt(self.value), self.currency)


# https://docs.python.org/3.7/library/decimal.html#recipes
def moneyfmt(value, places=2, curr='', sep=',', dp='.',
             pos='', neg='-', trailneg=''):
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    """
    q = Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    if places:
        build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))


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
