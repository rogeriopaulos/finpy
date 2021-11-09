import datetime as dt
import logging
import os
import urllib
from abc import ABC, abstractmethod

from pymongo import MongoClient
from pymongo.errors import BulkWriteError, ConnectionFailure
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from requests.models import Response

# Logging
# ------------------------------------------------------------------------------
log_format = '[%(asctime)s][%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
LOGGER = logging.getLogger('root')


# Database
# ------------------------------------------------------------------------------
class MongodbClient:

    username = urllib.parse.quote_plus(os.environ.get('MONGODB_USERNAME'))
    password = urllib.parse.quote_plus(os.environ.get('MONGODB_PASSWORD'))
    host = urllib.parse.quote_plus(os.environ.get('MONGODB_HOST'))
    port = urllib.parse.quote_plus(os.environ.get('MONGODB_PORT'))

    def client(self):
        return MongoClient(f'mongodb://{self.username}:{self.password}@{self.host}:{self.port}')


class BaseAPI(ABC):

    @abstractmethod
    def get_api(self):
        ...

    def save(self):
        try:
            cryptoapi = self.get_api()
            LOGGER.info(f'Get data from {cryptoapi.__str__()}')
            response = cryptoapi.make_request()
            data = response.json()
            timestamp = dt.datetime.now()
            data = [dict(item, **{'_created_at': timestamp, '_source': cryptoapi.__str__()}) for item in data]
            LOGGER.info(f'Request successful: "status_code": {response.status_code}, "count": {len(data)}')
            docs_count = self.create_mongo_docs(data, timestamp)
            LOGGER.info(f'Created {docs_count} docs at mongodb')
            return {"status_code": response.status_code, "count_docs": len(data)}
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            LOGGER.error('An error has occurred. Check traceback.')
            print(e)

    def create_mongo_docs(self, data, timestamp):
        try:
            client = MongodbClient().client()
            db = client['cryptosdb']
            cryptos = db.cryptos
            result = cryptos.insert_many(data)
            requests_timestamp = db.requests_timestamp
            requests_timestamp.insert_one({'requests_timestamp': timestamp})
            return len(result.inserted_ids)
        except (ConnectionFailure, BulkWriteError) as e:
            LOGGER.error('An error has occurred. Check traceback.')
            print(e)


class CryptoAPI(ABC):

    @abstractmethod
    def make_request(self) -> Response:
        ...


def send2mongo(api: BaseAPI) -> None:
    return api.save()
