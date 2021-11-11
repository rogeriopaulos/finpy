import math
import os

from requests import Session
from requests.models import Response

from fincryptos.core import BaseAPI, CryptoAPI


class CoinMarketCapCryptoAPI(CryptoAPI):

    base_url = os.environ.get('COINMARKETCAP_BASE_URL')
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': os.environ.get('COINMARKETCAP_API_KEY'),
    }
    collection_name = 'coinmarketcap'
    max_request_limit = 5000

    def __str__(self):
        return 'CoinMarketCap API'

    def get_total_currencies(self):
        response_data = self.make_request('map').json()
        if 'data' in response_data.keys():
            total_currencies = len(response_data.get('data'))
        return total_currencies

    def get_data(self) -> Response:
        total_currencies = self.get_total_currencies()

        if total_currencies > self.max_request_limit:
            intervals = self.get_intervals(total_currencies)

        # return self.make_request('listings/latest', self.parameters)
        return intervals

    def get_intervals(self, total_currencies):
        parts = math.ceil(total_currencies / self.max_request_limit)
        max_interval = int(total_currencies / parts)
        return [(i * max_interval + 1, ((i + 1) * max_interval) + 1) for i in range(parts)]

    def make_request(self, url_path, params=None) -> Response:
        url = f'https://{self.base_url}/v1/cryptocurrency/{url_path}'
        session = Session()
        session.headers.update(self.headers)
        if params is not None:
            response = session.get(url, params=self.parameters)
        else:
            response = session.get(url)
        return response


class CoinMarketCap(BaseAPI):

    api = CoinMarketCapCryptoAPI()

    def get_api_data(self) -> dict:
        data = self.api.get_data()
        return {
            'data': data['data'],
            'source': self.api.__str__(),
            'collection_name': self.api.collection_name,
            'status_code': data['status_code']
        }
