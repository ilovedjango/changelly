# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, request, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from .models import Payment, Wallet

from django.http import HttpResponse, Http404
# Create your views here.

def get_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



def index(request):
    ip_address = get_ip_address(request)
    q = Payment.objects.filter(ip_address=ip_address).count()

    if q > 0:
        payment = Payment.objects.get(ip_address=ip_address)
        try:
            toWallet = Wallet.objects.get(currency=payment.from_currency)
        except ObjectDoesNotExist:
            pass
        context = {"unique_id": payment.transaction_id,
                   "from_amount": payment.exchange_amount,
                   "hdn_from_currency": payment.from_currency,
                   "wallet": toWallet.address}
        return render(request, 'sending.html', context)
    else:
        return render(request, 'index.html')

@csrf_exempt
def GetAmount(request):
    global amount, fromCurrency, toCurrency, result
    if request.is_ajax():
        amount = request.POST.get('from_amount')
        fromCurrency = request.POST.get('from')
        toCurrency = request.POST.get('to')
        import hashlib
        import hmac
        import json
        import requests
        API_URL = 'https://api.changelly.com'
        API_KEY = '0839aac85630482ca0f69fb6971cb14c'
        API_SECRET = 'fa930a5559b67ff9e4d35aa741fa34aea9cea7b63e3fcf04cf2c687a2fcf13dc'
        message = {
            "jsonrpc": "2.0",
            "method": "getExchangeAmount",
            "params": {
                "from": fromCurrency,
                "to": toCurrency,
                "amount": amount,
            },
            "id": 1
        }
        serialized_data = json.dumps(message)
        sign = hmac.new(API_SECRET.encode('utf-8'), serialized_data.encode('utf-8'), hashlib.sha512).hexdigest()
        headers = {'api-key': API_KEY, 'sign': sign, 'Content-type': 'application/json'}
        response = requests.post(API_URL, headers=headers, data=serialized_data)
        response_data = response.json()
        print("===================================================")
        print("From amount: {}".format(amount))
        print("From currency: {}".format(fromCurrency))
        print("To currency: {}".format(toCurrency))
        print("Result: {}".format(response_data['result']))
        result = response_data['result']
        print("===================================================")
        print(response_data)
        print("===================================================")
        return HttpResponse(response_data['result'])


def processing(request):
        import datetime
        now = datetime.datetime.now()
        if request.POST:
            hdn_from_currency = request.POST.get('hdn_from_currency')
            if hdn_from_currency == '':
                hdn_from_currency = 'BTC'
            hdn_to_currency = request.POST.get('hdn_to_currency')
            if hdn_to_currency == '':
                hdn_to_currency = 'ETH'
            from_amount = request.POST.get('from_amount')
            to_amount = request.POST.get('to_amount')
            ip_address = get_ip_address(request)
            unique_id = get_random_string(length=12)
            new = Payment(pub_date=now, ip_address=ip_address, transaction_id=unique_id, exchange_amount=from_amount,
                          from_currency=hdn_from_currency, to_currency=hdn_to_currency, result_amount=to_amount,
                          confirmed='no')
            new.save()

        request.session['hdn_from_currency'] = hdn_from_currency
        request.session['hdn_to_currency'] = hdn_to_currency
        request.session['from_amount'] = from_amount
        request.session['to_amount'] = to_amount

        request.session['unique_id'] = unique_id

        context = {"hdn_from_currency": hdn_from_currency,
                   "hdn_to_currency": hdn_to_currency,
                   "from_amount": from_amount,
                   "to_amount": to_amount,}

        return render(request, 'processing.html', context)



def sendto(request):
    ip_address = get_ip_address(request)
    hdn_to_currency = request.session['hdn_to_currency']

    context = {"hdn_to_currency": hdn_to_currency}
    return render(request, 'sendto.html', context)


def confirmation(request):
    if request.POST:
        address = request.POST.get('address')
    hdn_from_currency = request.session['hdn_from_currency']
    hdn_to_currency = request.session['hdn_to_currency']
    from_amount = request.session['from_amount']
    to_amount = request.session['to_amount']

    context = {"hdn_from_currency": hdn_from_currency,
               "hdn_to_currency": hdn_to_currency,
               "from_amount": from_amount,
               "to_amount": to_amount,
               "address": address,}
    return render(request, 'confirmation.html', context)


def sending(request):
    unique_id = request.session['unique_id']
    hdn_from_currency = request.session['hdn_from_currency']
    hdn_to_currency = request.session['hdn_to_currency']
    from_amount = request.session['from_amount']
    to_amount = request.session['to_amount']

    wallet = Wallet.objects.get(currency=hdn_from_currency)

    context = {"unique_id": unique_id,
               "hdn_from_currency": hdn_from_currency,
               "hdn_to_currency": hdn_to_currency,
               "from_amount": from_amount,
               "to_amount": to_amount,
               "wallet": wallet.address,}
    return render(request, 'sending.html', context)