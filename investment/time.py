from collections import namedtuple


class Error(Exception):
    """Base class for exceptions in this module."""


class ParseMonthError(Error):
    """Raised when there is an error parsing a month value."""


_Month = namedtuple('Month', ['year', 'month', 'day'])


# TODO: switch to Python's date class
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

    DAYS_PER_MONTH = {
            1: 31,
            2: 28, # TODO
            3: 31,
            4: 30,
            5: 31,
            6: 30,
            7: 31,
            8: 31,
            9: 30,
            10: 31,
            11: 30,
            12: 31,
    }

    def succ(self):
        if self.day == self.DAYS_PER_MONTH[self.month]:
            if self.month == 12:
                return Month(self.year + 1, 1, 1)
            return Month(self.year, self.month + 1, 1)
        return Month(self.year, self.month, self.day + 1)

    def pred(self):
        if self.day == 1:
            if self.month == 1:
                return Month(self.year - 1, 12, 31)
            return Month(self.year, self.month - 1, self.DAYS_PER_MONTH[self.month-1])
        return Month(self.year, self.month, self.day - 1)

    @property
    def doy(self):
        val = self.day
        for i in range(1, self.month):
            val += self.DAYS_PER_MONTH[i]
        return val

    def __str__(self):
        return "%02d%s%04d" % (self.day, self.MONTHS.get(self.month, "ERR"), self.year)

    @classmethod
    def parse(cls, text):
        if len(text) != 9:
            raise ParseMonthError("Month must be 9 characters DDMMMYYYY")
        day = text[:2]
        month = text[2:5]
        year = text[5:]
        for k, v in cls.MONTHS.items():
            if v == month:
                return Month(int(year), k, int(day))
