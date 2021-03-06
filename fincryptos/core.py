import datetime as dt
import logging
import os
import urllib
from abc import ABC, abstractmethod

import telegram
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

    username = urllib.parse.quote_plus(str(os.environ.get('MONGODB_USERNAME')))
    password = urllib.parse.quote_plus(str(os.environ.get('MONGODB_PASSWORD')))
    host = urllib.parse.quote_plus(str(os.environ.get('MONGODB_HOST')))
    port = urllib.parse.quote_plus(str(os.environ.get('MONGODB_PORT')))

    def client(self):
        return MongoClient(f'mongodb://{self.username}:{self.password}@{self.host}:{self.port}')


# API
# ------------------------------------------------------------------------------
class BaseAPI(ABC):

    @abstractmethod
    def get_api_data(self):
        ...

    def save(self):
        try:
            api_data = self.get_api_data()
            source = api_data.get('source')
            status_code = api_data.get('status_code')
            LOGGER.info(f'Get data from {source}')
            timestamp = dt.datetime.now()

            data = [dict(item, **{'_created_at': timestamp, '_source': source})
                    for item in api_data.get('data')]
            count_data = len(data)
            LOGGER.info(f'Request successful: "status_code": {status_code}, "count": {count_data}')

            docs_count = self.create_mongo_docs(data, timestamp, api_data.get('collection_name'))
            LOGGER.info(f'Created {docs_count} docs at mongodb')

            return {"status_code": status_code, "count_docs": count_data}
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            LOGGER.error('An error has occurred. Check traceback.')
            print(e)

    def create_mongo_docs(self, data, timestamp, collection_name):
        try:
            client = MongodbClient().client()
            db = client['cryptosdb']
            collection = db[collection_name]
            result = collection.insert_many(data)
            requests_timestamp = db[f'{collection_name}_requests_timestamp']
            requests_timestamp.insert_one({'request_timestamp': timestamp})
            return len(result.inserted_ids)
        except (ConnectionFailure, BulkWriteError) as e:
            LOGGER.error('An error has occurred. Check traceback.')
            print(e)


class CryptoAPI(ABC):

    @abstractmethod
    def make_request(self) -> Response:
        ...


# Helpers
# ------------------------------------------------------------------------------
def send2mongo(api: BaseAPI) -> None:
    return api.save()


def clear_collections(collection_name):
    client = MongodbClient().client()

    db = client['cryptosdb']
    collection_data = db[collection_name]
    collection_timestamp = db[f'{collection_name}_requests_timestamp']

    LOGGER.info(f'Removing docs from "{collection_data}" and "{collection_timestamp}" collection')
    collection_data.delete_many({})
    collection_timestamp.delete_many({})


# Telegram
# ------------------------------------------------------------------------------
class Telegram:

    def __init__(self):
        self.token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    def send_message(self, msg):
        bot = telegram.Bot(token=self.token)
        if len(msg) > 4096:
            for x in range(0, len(msg), 4096):
                response = bot.send_message(self.chat_id, msg[x:x+4096], parse_mode=telegram.ParseMode.HTML)
        else:
            response = bot.send_message(self.chat_id, msg, parse_mode=telegram.ParseMode.HTML)
        return response.to_dict()
