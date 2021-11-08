from abc import ABC, abstractmethod

from pymongo.errors import BulkWriteError, ConnectionFailure

from .core import LOGGER, MongodbClient


class AlertBase(ABC):

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
    def run_alert(self):
        ...


class AlertStartCryptoWithLetter(AlertBase):

    def __init__(self, letter: str):
        self.letter = letter

    def run_alert(self):
        try:
            return [crypto['id'] for crypto in self.dataset if crypto['id'].startswith(self.letter)]
        except (ConnectionFailure, BulkWriteError) as e:
            LOGGER.error('An error has occurred. Check traceback.')
            print(e)


class RunAlerts:

    alerts = [AlertStartCryptoWithLetter('W')]

    def run_alerts(self) -> list:
        return [alert.run_alert() for alert in self.alerts]
