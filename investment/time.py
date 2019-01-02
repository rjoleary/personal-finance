from collections import namedtuple


class Error(Exception):
    """Base class for exceptions in this module."""


class ParseMonthError(Error):
    """Raised when there is an error parsing a month value."""


_Month = namedtuple('Month', ['year', 'month'])


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
