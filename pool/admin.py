# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy

from .models import Payment, Wallet
# Register your models here.

admin.site.site_header = 'Cryptocurrency administration'

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('pub_date', 'ip_address', 'exchange_amount', 'from_currency', 'to_currency', 'result_amount', 'confirmed')

admin.site.register(Payment, PaymentAdmin)

class WalletAdmin(admin.ModelAdmin):
    list_display = ('currency', 'address',)
admin.site.register(Wallet, WalletAdmin)