from fincryptos.bot import Telegram

from .alerts import AlertStartCryptoWithLetter


class RunAlerts:

    _filter_alerts = [
        AlertStartCryptoWithLetter('B')
    ]
    _bot = Telegram()

    def run_alerts(self):
        for alert in self._filter_alerts:
            if alert.need_alert():
                self._bot.send_message(alert.render_alert())
