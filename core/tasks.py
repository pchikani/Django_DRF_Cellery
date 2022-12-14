from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .models import Scripe
import requests
from decimal import *
from django.db import transaction

import datetime
import time

@shared_task(name = "update_scripes")
def update_price():
    with transaction.atomic():
        api_key = 'P9PL2RAXE6WZXR7L'
        scripes = Scripe.objects.all()
        for scripe in scripes:
            url = 'https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol=' + scripe.scripename + '&market=INR&interval=5min&apikey=' + api_key
            rc = requests.get(url)
            datac = rc.json()
            
            if 'Meta Data' in datac:
                last_refreshed = datac['Meta Data']['6. Last Refreshed']
                curr_price = datac['Time Series Crypto (5min)'][last_refreshed]['1. open']
                high_price = datac['Time Series Crypto (5min)'][last_refreshed]['2. high']
                low_price = datac['Time Series Crypto (5min)'][last_refreshed]['3. low']
                close_price = datac['Time Series Crypto (5min)'][last_refreshed]['4. close']
                volume = datac['Time Series Crypto (5min)'][last_refreshed]['5. volume']
                scripe.currprice = Decimal(curr_price)
                scripe.highprice = Decimal(high_price)
                scripe.lowprice = Decimal(low_price)
                scripe.closeprice = Decimal(close_price)
                scripe.volume = volume
                scripe.save()
