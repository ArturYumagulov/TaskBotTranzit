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
                    admin_ids=list(map(int, env.list('ADMIN_IDS')))))


DELETE_MESSAGE_TIMER = 7

CONSTANT_COMMENT_ID = 1

API_BASE_URL = "http://192.168.80.65/api/v1/"
# API_BASE_URL = "http://127.0.0.1:8000/api/v1/"

AUTH_DATA = {'username': env('BOT_USERNAME'), 'password': env('PASSWORD')}

API_METHODS = {
    'tasks': "tasks/",
    'workers': "workers/",
    'workers_f': "worker_f/",
    'partner-worker_f': 'partner-worker_f/',
    'result-data_f': 'result-data_f/',
    'result': 'result/',
    'result-data': 'result-data/',
    'supervisors': 'supervisors/',
    'auth': 'token-auth/'
}

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(filename)s:%(lineno)d #%(levelname)-8s '
                      '[%(asctime)s] - %(name)s - %(message)s'
        }
    },
    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': 'logs/logfile.txt'
        }


    },
    'loggers': {
        'bot': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': 'INFO',
            'propagate': False
        },
        'handlers.done_handlers': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': 'INFO',
            'propagate': False
        },
        'handlers.dont_handler': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': 'INFO',
            'propagate': False
        },
        'handlers.forward_handlers': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': 'INFO',
            'propagate': False
        },
        'handlers.other_handlers': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': 'INFO',
            'propagate': False
        },
        'database.database': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
