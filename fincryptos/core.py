from abc import ABC, abstractmethod

from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from requests.models import Response


class BaseAPI(ABC):

    @abstractmethod
    def get_api(self):
        ...

    def save(self):
        try:
            cryptoapi = self.get_api()
            response = cryptoapi.make_request()
            # TODO: Implementar aqui a lógica de persistir os dados obtidos da API
            return response.json()
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)


class CryptoAPI(ABC):

    @abstractmethod
    def make_request(self) -> Response:
        ...


def send2mongo(api: BaseAPI) -> None:
    print(api.save())
