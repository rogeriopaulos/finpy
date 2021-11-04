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
            LOGGER.info(f'Request successful: "status_code": {response.status_code}, "count": {len(data)}')
            docs_count = self.create_mongo_docs(data)
            LOGGER.info(f'Created {docs_count} docs at mongodb')
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            LOGGER.error('An error has occurred. Check traceback.')
            print(e)

    def create_mongo_docs(self, data):
        username = urllib.parse.quote_plus(os.environ.get('MONGODB_USERNAME'))
        password = urllib.parse.quote_plus(os.environ.get('MONGODB_PASSWORD'))
        host = urllib.parse.quote_plus(os.environ.get('MONGODB_HOST'))
        port = urllib.parse.quote_plus(os.environ.get('MONGODB_PORT'))

        try:
            client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}')
            db = client['cryptosdb']
            db['currencies']
            cryptos = db.cryptos
            result = cryptos.insert_many(data)
            return len(result.inserted_ids)
        except (ConnectionFailure, BulkWriteError) as e:
            LOGGER.error('An error has occurred. Check traceback.')
            print(e)


class CryptoAPI(ABC):

    @abstractmethod
    def make_request(self) -> Response:
        ...


def send2mongo(api: BaseAPI) -> None:
    print(api.save())
