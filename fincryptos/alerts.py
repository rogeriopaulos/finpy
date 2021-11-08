from abc import ABC, abstractmethod

from pymongo.errors import BulkWriteError, ConnectionFailure

from .bot import Telegram
from .core import LOGGER, MongodbClient


class BaseAlert(ABC):

    def client(self):
        return MongodbClient().client()

    @property
    def dataset(self) -> list:
        client = self.client()
        db = client['cryptosdb']
        requests_timestamp = db.requests_timestamp
        last_request_timestamp = [r['requests_timestamp'] for r in requests_timestamp.find()][-1]
        cryptos = db.cryptos
        return [crypto for crypto in cryptos.find({'_created_at': last_request_timestamp})]

    @abstractmethod
    def create_alert(self):
        ...


class AlertStartCryptoWithLetter(BaseAlert):

    def __init__(self, letter: str):
        self.letter = letter

    def create_alert(self):
        try:
            result = [crypto['id'] for crypto in self.dataset if crypto['id'].startswith(self.letter)]
            return ' '.join(result)
        except (ConnectionFailure, BulkWriteError) as e:
            LOGGER.error('An error has occurred. Check traceback.')
            print(e)


class RunAlerts:

    _filter_alerts = [
        AlertStartCryptoWithLetter('B')
    ]
    _bot = Telegram()

    def run_alerts(self):
        for alert in self._filter_alerts:
            self._bot.send_message(alert.create_alert())
