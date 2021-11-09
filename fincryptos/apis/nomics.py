import os

import requests
from requests.models import Response

from fincryptos.core import BaseAPI, CryptoAPI


class NomicsCryptoAPI(CryptoAPI):

    base_url = os.environ.get('NOMICS_BASE_URL')
    collection_name = 'nomics'

    def __init__(self, parameter):
        self.parameters = parameter

    def __str__(self):
        return 'Nomics Cryptocurrency & Bitcoin API'

    def make_request(self) -> Response:
        url = f'{self.base_url}/currencies/ticker'
        return requests.get(url, params=self.parameters)


class Nomics(BaseAPI):

    def get_api_data(self) -> dict:
        parameters = {
            'key': os.environ.get('NOMICS_API_KEY'),
            'sort': 'first_priced_at',
            'interval': '1h,1d',
            'status': 'active'
        }
        api = NomicsCryptoAPI(parameters)
        response = api.make_request()
        data = response.json()
        return {
            'data': data,
            'source': api.__str__(),
            'collection_name': api.collection_name,
            'status_code': response.status_code
        }
