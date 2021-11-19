import telegram
from telegram import Update
from telegram.ext import CallbackContext

from fincryptos.alerts.alerts import AlertCurrencyGeneralInfo


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def info(update: Update, context: CallbackContext):
    currencies_args = context.args
    for currency in currencies_args:
        alert = AlertCurrencyGeneralInfo(currency.upper())
        msg = alert.render_alert()
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=telegram.ParseMode.HTML)
