import logging
import httpx
from environs import Env

env = Env()
Env.read_env()


class TelegramLogsHandler(logging.Handler):
    def emit(self, record):
        update_id = env("ADMIN_IDS")
        log_entry = self.format(record)
        url = f'https://api.telegram.org/bot{env("LOGS_BOT_TOKEN")}/sendMessage?chat_id={update_id}&text={log_entry}&parse_mode=HTML'
        httpx.get(url)
