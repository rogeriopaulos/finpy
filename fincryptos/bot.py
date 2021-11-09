import os

import telegram


class Telegram:

    def __init__(self):
        self.token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    def send_message(self, msg):
        bot = telegram.Bot(token=self.token)
        if len(msg) > 4096:
            for x in range(0, len(msg), 4096):
                bot.send_message(self.chat_id, msg[x:x+4096], parse_mode=telegram.ParseMode.HTML)
        else:
            bot.send_message(self.chat_id, msg, parse_mode=telegram.ParseMode.HTML)
