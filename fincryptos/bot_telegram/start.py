import logging

from telegram.ext import CommandHandler, Updater

from fincryptos.bot_telegram.handlers import info, start
from fincryptos.core import Telegram

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


info_telegram = Telegram()
updater = Updater(token=info_telegram.token, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
info_handler = CommandHandler('info', info)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(info_handler)

updater.start_polling()
