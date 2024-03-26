import json
import logging
from config_data import config
import httpx
from environs import Env

from config_data.config import API_BASE_URL

logger = logging.getLogger(__name__)

env = Env()
Env.read_env()


def clear_date(data):
    """Функция очистки даты от символов"""
    return data.replace("T", " ").replace("Z", "")


def comparison(controller_list, supervisor_list, author_list, worker_list, partner_list=None, head_list=None):
    """Функция сравнения, для вывода нужных адресатов для переадресации задачи"""

    result_list = []

    if partner_list is not None:
        if author_list['controller'] and partner_list['code'] != supervisor_list['code']:
            result_list.append(supervisor_list)
            result_list.append(author_list)
            result_list.append(partner_list)
            result_list.append(head_list)
        elif author_list['code'] == config.SOFT_COLLECTION_USER_CODE:
            result_list.append(supervisor_list)
            result_list.append(controller_list)
            result_list.append(partner_list)
            result_list.append(head_list)
        elif author_list['code'] == supervisor_list['code'] and supervisor_list['code'] != partner_list['code']:
            result_list.append(controller_list)
            result_list.append(author_list)
            result_list.append(partner_list)
            result_list.append(head_list)
        elif supervisor_list['code'] == partner_list['code']:
            result_list.append(controller_list)
            result_list.append(supervisor_list)
            result_list.append(head_list)
        elif author_list['code'] == partner_list['code']:
            result_list.append(partner_list)
            result_list.append(controller_list)
            result_list.append(supervisor_list)
            result_list.append(head_list)
        elif author_list['code'] == supervisor_list['code']:
            result_list.append(controller_list)
            result_list.append(author_list)
            result_list.append(head_list)
        elif partner_list['code'] == worker_list['code']:
            result_list.append(controller_list)
            result_list.append(author_list)
            result_list.append(supervisor_list)
            result_list.append(head_list)
        else:
            result_list.append(controller_list)
            result_list.append(supervisor_list)
            result_list.append(author_list)
            result_list.append(partner_list)
            result_list.append(head_list)

    else:
        if author_list['controller']:
            result_list.append(supervisor_list)
            result_list.append(author_list)
            result_list.append(head_list)
        elif author_list['code'] == config.SOFT_COLLECTION_USER_CODE:
            result_list.append(supervisor_list)
            result_list.append(controller_list)
            result_list.append(head_list)
        elif author_list['code'] == supervisor_list['code']:
            result_list.append(controller_list)
            result_list.append(author_list)
            result_list.append(head_list)
        elif author_list['code'] == controller_list['code']:
            result_list.append(controller_list)
            result_list.append(supervisor_list)
            result_list.append(head_list)
        else:
            result_list.append(controller_list)
            result_list.append(supervisor_list)
            result_list.append(author_list)
            result_list.append(head_list)

    return result_list


def del_ready_task(chat_id, message_id):
    r = httpx.get(
        f'https://api.telegram.org/bot{env.str("BOT_TOKEN")}/deleteMessage?chat_id={chat_id}&message_id={message_id}')
    if r.json()['ok']:
        logger.info(f"{chat_id}- {r.json()['result']} - "
                    f"- {message_id} удалено сообщение - 201")
        return True
    else:
        logger.error(f"{chat_id} - {r.json()['description']}"
                     f"- не удалено - 400")
        return False


def update_task_message_id(message_id, task_number):
    update_task = {
        "number": task_number,
        "message_id": message_id,
    }

    r = httpx.put(
        f"{API_BASE_URL}task-message-update/", data=update_task)

    if r.status_code == 201:
        logger.info(f"{task_number}- {r.json()['result']} - "
                    f"- {message_id} обновлено - 201")
        return True
    else:
        logger.error(f"{task_number} - {r.json()}"
                     f"- {message_id} не обновлено - {r.status_code}")
        return False


if __name__ == '__main__':
    author = {'list': 'author', 'code': "SoftCollect", 'controller': False}
    worker = {'list': 'worker', 'code': "W", 'controller': False}
    controller = {'list': 'controller', 'code': 'C', 'controller': True}
    supervisor = {'list': 'supervisor', 'code': "S", 'controller': False}
    partner = {'list': 'partner', 'code': "P", 'controller': False}

    print(comparison(
        controller_list=controller,
        author_list=author,
        supervisor_list=supervisor,
        partner_list=partner,
        worker_list=worker
    ))
