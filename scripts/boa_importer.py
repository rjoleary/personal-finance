#!python

from collections import namedtuple
from datetime import datetime
from decimal import Decimal
import csv
import os
import sys
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
django.setup()
from models.models import Account, Category, Transaction
from django.db.transaction import atomic
from django.utils.timezone import make_aware


_BoaTransaction = namedtuple('BoaTransaction', [
    'posted_date',
    'reference_number',
    'payee',
    'address',
    'amount',
])


class BoaTransaction(_BoaTransaction):
    @classmethod
    def from_csv(cls, row):
        return cls(
                make_aware(datetime.strptime(row[0], '%m/%d/%Y')),
                int(row[1]),
                row[2],
                row[3],
                Decimal(row[4]),
        )

    def to_transaction(self):
        return Transaction(
                date=self.posted_date,
                description=self.payee,
                amount=self.amount,
        )


def Parse(fileobj):
    expected_header = 'Posted Date,Reference Number,Payee,Address,Amount'
    if fileobj.read(len(expected_header)) != expected_header:
        raise RuntimeError('This is not a BOA file or the CSV header has changed')
    fileobj.seek(0)

    reader = csv.reader(fileobj)
    next(reader)
    return [BoaTransaction.from_csv(row) for row in reader]


def ParseFile(filename):
    with open(filename, 'r') as fileobj:
        return Parse(fileobj)


@atomic
def SaveAll(account, transactions):
    for t in transactions:
        t = t.to_transaction()
        t.account = account
        t.save()


def main():
    account_name = sys.argv[1]
    account = Account.objects.get(name=account_name)

    for arg in sys.argv[2:]:
        print('Reading %s...' % arg)
        transactions = ParseFile(arg)
        print('  Found %s transactions' % len(transactions))
        print('  Writing to database...')
        SaveAll(account, transactions)
        print('  Saved %s transactions' % len(transactions))


if __name__ == '__main__':
    main()
