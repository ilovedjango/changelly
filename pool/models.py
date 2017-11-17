# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Payment(models.Model):
    pub_date = models.DateTimeField('date published')
    ip_address = models.GenericIPAddressField()
    transaction_id = models.CharField(max_length=30, blank=True)
    exchange_amount = models.CharField(max_length=30, blank=True)
    from_currency = models.CharField(max_length=30, blank=True)
    to_currency = models.CharField(max_length=30, blank=True)
    result_amount = models.CharField(max_length=30, blank=True)
    confirmed = models.CharField(max_length=30, blank=True)

    def __unicode__(self):
        return self.from_currency + self.exchange_amount


class Wallet(models.Model):
    currency = models.CharField(max_length=15)
    address = models.CharField(max_length=100)

    def __unicode__(self):
        return self.currency, self.address