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

    def __init__(self, parameter):
        self.parameters = parameter

    def make_request(self) -> Response:
        url = f'https://{self.base_url}/v1/cryptocurrency/listings/latest'
        session = Session()
        session.headers.update(self.headers)
        return session.get(url, params=self.parameters)


class CoinMarketCap(BaseAPI):

    def get_api(self) -> CryptoAPI:
        parameters = {
            'start': '1',
            'limit': '5000',
            'convert': 'USD'
        }
        return CoinMarketCapCryptoAPI(parameters)
