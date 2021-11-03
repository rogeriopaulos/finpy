from fincryptos.core import send2mongo
from fincryptos.cryptoapis.nomics import Nomics


def send_nomics_data2mongo():
    send2mongo(Nomics())
