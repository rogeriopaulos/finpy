from .base import BaseAlert


class AlertStartCryptoWithLetter(BaseAlert):

    template_name = 'AlertStartCryptoWithLetter.html'

    def __init__(self, letter: str):
        self.letter = letter

    def need_alert(self):
        content = self.get_content()
        return True if len(content) > 0 else False

    def get_title(self):
        return f'[ALERTA] Cryptomoedas que começam com a letra "{self.letter}"'

    def get_content(self):
        result = [crypto['id'] for crypto in self.dataset if crypto['id'].startswith(self.letter)]
        return ' '.join(result)

    def get_source(self):
        return self.dataset[0]['_source']
