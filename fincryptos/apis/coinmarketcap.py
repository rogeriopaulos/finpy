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

    def __init__(self):
        self.parameters = {
            'start': '1',
            'limit': self.get_limit(),
            'convert': 'USD'
        }

    def __str__(self):
        return 'CoinMarketCap API'

    def get_limit(self):
        return '5000'

    def make_request(self, url_path, params=None) -> Response:
        url = f'https://{self.base_url}/v1/cryptocurrency/{url_path}'
        session = Session()
        session.headers.update(self.headers)
        if params is not None:
            response = session.get(url, params=self.parameters)
        else:
            response = session.get(url)
        return response

    def get_data(self) -> Response:
        return self.make_request('listings/latest', self.parameters)


class CoinMarketCap(BaseAPI):

    api = CoinMarketCapCryptoAPI()

    def get_api_data(self) -> dict:
        response = self.api.get_data()
        data = response.json()
        return {
            'data': data['data'],
            'source': self.api.__str__(),
            'collection_name': self.api.collection_name,
            'status_code': response.status_code
        }
