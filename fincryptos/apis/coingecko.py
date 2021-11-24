from pycoingecko import CoinGeckoAPI

from fincryptos.core import BaseAPI, CryptoAPI


class CoinGeckoCryptoAPI(CryptoAPI):

    collection_name = 'coingecko'

    def __init__(self):
        self.cg = CoinGeckoAPI()

    def __str__(self):
        return 'CoinGecko API'

    def get_data(self) -> dict:
        response_data = self.make_request()
        return {'data': response_data, 'status_code': 200}

    def make_request(self):
        return self.cg.get_coins_list()


class CoinGecko(BaseAPI):

    api = CoinGeckoCryptoAPI()

    def get_api_data(self) -> dict:
        data = self.api.get_data()
        return {
            'data': data.get('data'),
            'source': self.api.__str__(),
            'collection_name': self.api.collection_name,
            'status_code': data.get('status_code')
        }
