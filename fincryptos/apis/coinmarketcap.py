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

    def __init__(self, parameter):
        self.parameters = parameter

    def __str__(self):
        return 'CoinMarketCap API'

    def make_request(self) -> Response:
        url = f'https://{self.base_url}/v1/cryptocurrency/listings/latest'
        session = Session()
        session.headers.update(self.headers)
        return session.get(url, params=self.parameters)


class CoinMarketCap(BaseAPI):

    def get_api_data(self) -> dict:
        parameters = {
            'start': '1',
            'limit': '5000',
            'convert': 'USD'
        }
        api = CoinMarketCapCryptoAPI(parameters)
        response = api.make_request()
        data = response.json()
        return {
            'data': data['data'],
            'source': api.__str__(),
            'collection_name': api.collection_name,
            'status_code': response.status_code
        }
