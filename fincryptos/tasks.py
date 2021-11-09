import os

from celery import Celery
from celery.schedules import crontab

from fincryptos.alerts.runner import RunAlerts
from fincryptos.apis.nomics import Nomics
from fincryptos.core import send2mongo

redis_url = os.environ.get('REDIS_URL')

app = Celery('fyncriptos', broker=redis_url)
app.conf.result_backend = redis_url
app.conf.timezone = 'America/Fortaleza'


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Requests to nomics api frequency
    sender.add_periodic_task(crontab(minute='*/15'), send_nomics_data2mongo.s())


@app.task
def send_nomics_data2mongo():
    result = send2mongo(Nomics())
    if result.get('status_code') == 200:
        RunAlerts().run_alerts()
    return result
