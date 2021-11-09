from abc import ABC, abstractmethod

from jinja2 import Environment, PackageLoader, select_autoescape
from pymongo.errors import BulkWriteError, ConnectionFailure

from fincryptos.core import LOGGER, MongodbClient


class BaseAlert(ABC):

    template_name = None

    def client(self):
        return MongodbClient().client()

    @property
    def dataset(self) -> list:
        try:
            client = self.client()
            db = client['cryptosdb']
            requests_timestamp = db.requests_timestamp
            last_request_timestamp = [r['requests_timestamp'] for r in requests_timestamp.find()][-1]
            cryptos = db.cryptos
            return [crypto for crypto in cryptos.find({'_created_at': last_request_timestamp})]
        except (ConnectionFailure, BulkWriteError) as e:
            LOGGER.error('An error has occurred. Check traceback.')
            print(e)

    @abstractmethod
    def need_alert(self):
        ...

    @abstractmethod
    def get_title(self):
        ...

    @abstractmethod
    def get_content(self):
        ...

    @abstractmethod
    def get_source(self):
        ...

    def render_alert(self):
        env = Environment(loader=PackageLoader("fincryptos"), autoescape=select_autoescape())
        template = env.get_template(self.template_name)
        return template.render(title=self.get_title(), content=self.get_content(), source=self.get_source())
