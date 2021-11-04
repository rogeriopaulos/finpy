import os

import requests
from requests.models import Response

from fincryptos.core import BaseAPI, CryptoAPI


class NomicsCryptoAPI(CryptoAPI):

    base_url = os.environ.get('NOMICS_BASE_URL')

    def __init__(self, parameter):
        self.parameters = parameter

    def __str__(self):
        return 'Nomics Cryptocurrency & Bitcoin API'

    def make_request(self) -> Response:
        url = f'{self.base_url}/currencies/ticker'
        return requests.get(url, params=self.parameters)


class Nomics(BaseAPI):

    def get_api(self) -> CryptoAPI:
        parameters = {
            'key': os.environ.get('NOMICS_API_KEY'),
            # 'ids': 'BTC,ETH,ADA,DOT,BNB',
            'sort': 'first_priced_at',
            # 'per-page': 100,
            # 'page': 1,
            'interval': '1h,1d',
            'status': 'active'
        }
        return NomicsCryptoAPI(parameters)
