from .base import BaseAlert


class AlertStartCryptoWithLetter(BaseAlert):

    template_name = 'AlertStartCryptoWithLetter.html'
    collection_data = 'nomics'

    def __init__(self, letter: str):
        self.letter = letter

    def need_alert(self):
        content = self.get_content()
        return True if len(content) > 0 else False

    def get_title(self):
        return f'[ALERTA] Cryptomoedas que começam com a letra "{self.letter}"'

    def get_content(self):
        dataset = self.get_last_currencies()
        result = [crypto['id'] for crypto in dataset if crypto['id'].startswith(self.letter)]
        return ' '.join(result)

    def get_source(self):
        return self.dataset[0]['_source']


class AlertCurrencyGeneralInfo(BaseAlert):

    template_name = 'AlertCurrencyGeneralInfo.html'
    collection_data = 'nomics'

    def __init__(self, id: str):
        self.id = id

    def need_alert(self):
        content = list(self.get_content().values())
        return True if len(content) > 0 else False

    def get_title(self):
        return f'"{self.id.upper()}" INFO'

    def get_content(self):
        content = self.get_last_currency_by_id(self.id)

        datetimes_convert_fields = [
            'price_date', 'price_timestamp', 'first_candle', 'first_trade', 'first_order_book'
        ]
        for field in datetimes_convert_fields:
            datetime_obj = self.strdatetime2datetime(content.get(field))
            content[field] = datetime_obj

        content['price'] = float(content['price'])

        fields_large_numbers = ['circulating_supply', 'market_cap', 'max_supply']
        for field in fields_large_numbers:
            if field in content.keys():
                float_num = float(content[field])
                content[field] = "{:,}".format(float_num)

        return content

    def get_source(self):
        return self.get_content().get('_source')
