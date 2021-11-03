from fincryptos.core import BaseAPI


def send2mongo(api: BaseAPI) -> None:
    print(api.save())
