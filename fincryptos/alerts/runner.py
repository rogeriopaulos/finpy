from fincryptos.bot import Telegram


def send_alerts_if_need(alerts: list):
    for alert in alerts:
        if alert.need_alert():
            bot = Telegram()
            return bot.send_message(alert.render_alert())
