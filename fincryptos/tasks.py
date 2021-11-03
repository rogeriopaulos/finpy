import os

from celery import Celery

from fincryptos.apis.nomics import Nomics
from fincryptos.core import send2mongo

redis_url = os.environ.get('REDIS_URL')

app = Celery('fyncriptos', broker=redis_url)
app.conf.result_backend = redis_url


@app.task
def send_nomics_data2mongo():
    send2mongo(Nomics())
