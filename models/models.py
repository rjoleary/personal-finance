from django.db import models


class Account(models.Model):
    name     = models.CharField(max_length=30)
    currency = models.CharField(max_length=3)


class Category(models.Model):
    name = models.CharField(max_length=255)


class Transaction(models.Model):
    created     = models.DateTimeField(auto_now_add=True)
    date        = models.DateTimeField()
    amount      = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    payee       = models.CharField(max_length=255, blank=True)
    account     = models.ForeignKey(Account, on_delete=models.CASCADE)
    category    = models.ForeignKey(Category, on_delete=None, null=True)
