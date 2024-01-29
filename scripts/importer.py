#!/usr/bin/env python

# First create an account:
#     ./manage.py
#     from models.models import *
#     Account(name="Credit Card", currency="USD").save()
#
# Usage:
#     scripts/importer.py 'Credit Card' statements/*

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

def _int_or_none(x):
    try:
        return int(x)
    except ValueError:
        return None


_BoaTransaction = namedtuple('BoaTransaction', [
    'posted_date',
    'reference_number',
    'payee',
    'address',
    'amount',
])

class BoaTransaction(_BoaTransaction):
    header = 'Posted Date,Reference Number,Payee,Address,Amount'

    @classmethod
    def from_csv(cls, row):
        return cls(
                posted_date=make_aware(datetime.strptime(row[0], '%m/%d/%Y')),
                reference_number=_int_or_none(row[1]),
                payee=row[2],
                address=row[3],
                amount=Decimal(row[4]),
        )

    def to_transaction(self, account):
        return Transaction(
                account=account,
                date=self.posted_date,
                description=self.payee,
                amount=self.amount,
        )


_ChaseTransaction = namedtuple('ChaseTransaction', [
    'transaction_date',
    'post_date',
    'description',
    'category',
    'type',
    'amount',
    'memo',
])

class ChaseTransaction(_ChaseTransaction):
    header = 'Transaction Date,Post Date,Description,Category,Type,Amount,Memo'

    @classmethod
    def from_csv(cls, row):
        return cls(
                transaction_date=make_aware(datetime.strptime(row[0], '%m/%d/%Y')),
                post_date=make_aware(datetime.strptime(row[1], '%m/%d/%Y')),
                description=row[2],
                category=row[3],
                type=row[4],
                amount=Decimal(row[5]),
                memo=row[6],
        )

    def to_transaction(self, account):
        return Transaction(
                account=account,
                date=self.post_date,
                description=self.description,
                amount=self.amount,
        )


def Parse(fileobj):
    # Check which parser matches the header.
    header = fileobj.readline().strip()
    parsers = [p for p in [BoaTransaction, ChaseTransaction] if p.header == header]
    if len(parsers) == 0:
        raise RuntimeError('The file header %r is unrecognized' % header)
    if len(parsers) > 1:
        raise RuntimeError('The file header %r matches multiple parsers' % header)
    fileobj.seek(0)
    parser = parsers[0]

    reader = csv.reader(fileobj)
    next(reader)  # skip the header
    return [parser.from_csv(row) for row in reader]


def ParseFile(filename):
    with open(filename, 'r') as fileobj:
        return Parse(fileobj)


@atomic
def SaveAll(account, transactions):
    return Transaction.objects.bulk_create([t.to_transaction(account) for t in transactions])


def main():
    account_name = sys.argv[1]
    account = Account.objects.get(name=account_name)

    total_transactions = []
    for arg in sys.argv[2:]:
        print('Reading %s...' % arg)
        new_transactions = ParseFile(arg)
        print('  Found %s transactions' % len(new_transactions))
        total_transactions += new_transactions

    print('Writing to database...')
    SaveAll(account, total_transactions)
    print('Saved %s transactions' % len(total_transactions))


if __name__ == '__main__':
    main()
