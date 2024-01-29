Scripts for tracking personal finance in a sqlite database.

Setup:

    ./setup.sh

Querying:

    $ source env/bin/activate
    $ ./manage.py shell
    >>> from models.models import *
    >>> from django.db.models import Sum
    >>> Transaction.objects.filter(description__iregex=r'lyft').aggregate(total=Sum('amount'))
