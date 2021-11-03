import os

from celery import Celery
from celery.schedules import crontab

from fincryptos.apis.nomics import Nomics
from fincryptos.core import send2mongo

redis_url = os.environ.get('REDIS_URL')

app = Celery('fyncriptos', broker=redis_url)
app.conf.result_backend = redis_url
app.conf.timezone = 'America/Fortaleza'


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls every minute
    sender.add_periodic_task(crontab(minute='*/1'), send_nomics_data2mongo.s())


@app.task
def send_nomics_data2mongo():
    send2mongo(Nomics())
