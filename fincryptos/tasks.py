import os

from celery import Celery
from celery.schedules import crontab

from fincryptos.alerts.runner import RunAlerts
from fincryptos.apis.nomics import Nomics
from fincryptos.core import clear_collection, send2mongo

redis_url = os.environ.get('REDIS_URL')

app = Celery('fyncriptos', broker=redis_url)
app.conf.result_backend = redis_url
app.conf.timezone = 'America/Fortaleza'


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Requests to nomics api frequency every minute
    sender.add_periodic_task(crontab(minute='*/1'), send_nomics_data2mongo.s())

    # Clear mongodb cryptos collection every day at midnight
    sender.add_periodic_task(crontab(minute=0, hour=0), clear_mongo_collection.s())


@app.task
def send_nomics_data2mongo():
    result = send2mongo(Nomics())
    if result.get('status_code') == 200:
        send_alerts.delay()
    return result


@app.task
def send_alerts():
    RunAlerts().run_alerts()


@app.task
def clear_mongo_collection():
    clear_collection()
