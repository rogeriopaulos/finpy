import os

from celery import Celery
from celery.schedules import crontab

from fincryptos.alerts.alerts import AlertStartCryptoWithLetter
from fincryptos.alerts.runner import send_alerts_if_need
from fincryptos.apis.coinmarketcap import CoinMarketCap
from fincryptos.apis.nomics import Nomics
from fincryptos.core import clear_collections, send2mongo

# Configs
# ------------------------------------------------------------------------------
redis_url = os.environ.get('REDIS_URL')

app = Celery('fyncriptos', broker=redis_url)
app.conf.result_backend = redis_url
app.conf.timezone = 'America/Fortaleza'


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Requests to nomics api frequency every minute
    sender.add_periodic_task(crontab(minute='*/1'), send_nomics_data2mongo.s())

    # Clear mongodb cryptos collection once week -> on sundays
    sender.add_periodic_task(crontab(day_of_week=0), clear_nomics_collection.s())
    sender.add_periodic_task(crontab(day_of_week=0), clear_cmc_collection.s())


# Mongodb Tasks
# ------------------------------------------------------------------------------
@app.task
def send_nomics_data2mongo():
    result = send2mongo(Nomics())
    if result.get('status_code') == 200:
        send_nomics_alerts_after_save.delay()
    return result


@app.task
def send_coinmaeketcap_data2mongo():
    result = send2mongo(CoinMarketCap())
    return result


@app.task
def clear_nomics_collection():
    clear_collections('nomics')


@app.task
def clear_cmc_collection():
    clear_collections('coinmarketcap')


# Alerts Tasks
# ------------------------------------------------------------------------------
@app.task
def send_nomics_alerts_after_save():
    alert1 = AlertStartCryptoWithLetter('B')

    alerts = [alert1]
    response = send_alerts_if_need(alerts)
    return response
