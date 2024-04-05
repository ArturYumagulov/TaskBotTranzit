import logging.config
from dataclasses import dataclass

from environs import Env

env = Env()
Env.read_env()


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    env.read_env(path)
    return Config(tg_bot=TgBot(
                    token=env('BOT_TOKEN'),
                    admin_ids=list(map(int, env.list('ADMIN_IDS')))
    ))


DELETE_MESSAGE_TIMER = 7

CONSTANT_COMMENT_ID = 2

SOFT_COLLECTION_USER_CODE = "SoftCollect"

CENSUS = '000000004'

API_BASE_URL = env('API_BASE_URL')

TASK_GROUP = {
    '000000001': 'Pазработка Контрагента',
    '000000002': 'Кредитный Контроль',
    '000000004': 'Сенсус',
}

API_TOKEN = env('API_TOKEN')

API_METHODS = {
    'tasks': "tasks/",
    'workers': "workers/",
    'workers_f': "worker_f/",
    'partner-worker_f': 'partner-worker_f/',
    'result-data_f': 'result-data_f/',
    'result': 'result/',
    'result-data': 'result-data/',
    'supervisors': 'supervisors/',
    'auth': 'token-auth/',
    'worker_detail': 'workers/',
    'supervisor_detail': 'supervisors/'
}

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(filename)s:%(lineno)d #%(levelname)-8s '
                      '[%(asctime)s] - %(name)s - %(message)s'
        },
        'my_verbose': {
            'format': 'TASK_BOT - %(filename)s:%(lineno)d - <b>%(levelname)-8s</b> - '
                      '<i> [%(asctime)s]</i> - %(message)s'
        }
    },
    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': 'logs/logfile.txt'
        },
        'telegram_warning': {
            'class': 'services.log_handlers.TelegramLogsHandler',
            'formatter': 'my_verbose',
            'level': 'WARNING'
        },
        'telegram_info': {
            'class': 'services.log_handlers.TelegramLogsHandler',
            'formatter': 'my_verbose',
            'level': 'INFO'
        }
    },
    'loggers': {
        'bot': {
            'handlers': ['stream_handler', 'file_handler', 'telegram_info', 'telegram_warning'],
            'level': 'INFO',
            'propagate': False
        },
        'handlers.done_handlers': {
            'handlers': ['stream_handler', 'file_handler', 'telegram_warning'],
            'level': 'INFO',
            'propagate': False
        },
        'handlers.dont_handler': {
            'handlers': ['stream_handler', 'file_handler', 'telegram_warning'],
            'level': 'INFO',
            'propagate': False
        },
        'handlers.forward_handlers': {
            'handlers': ['stream_handler', 'file_handler', 'telegram_warning'],
            'level': 'INFO',
            'propagate': False
        },
        'handlers.other_handlers': {
            'handlers': ['stream_handler', 'file_handler', 'telegram_warning'],
            'level': 'INFO',
            'propagate': False
        },
        'database.database': {
            'handlers': ['stream_handler', 'file_handler', 'telegram_warning'],
            'level': 'INFO',
            'propagate': False
        },
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
