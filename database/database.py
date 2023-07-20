import logging
import json
import requests
from config_data.config import API_BASE_URL, API_METHODS, CONSTANT_COMMENT_ID, API_TOKEN

from config_data.config import CONSTANT_COMMENT_ID
from services.utils import comparison

logger = logging.getLogger(__name__)


def get_token():
    # r = requests.post(url=f"{API_BASE_URL}{API_METHODS['auth']}", data={'username': AUTH_DATA['username'],
    #                                                                     'password': AUTH_DATA['password']})
    # logger.info(f"GET запрос {API_METHODS['auth']} - {r.status_code}")
    # return r.json()['token']
    return API_TOKEN


def get_task_number(task_number):
    r = requests.get(url=f"{API_BASE_URL}{API_METHODS['tasks']}{task_number}/",
                     headers={'Authorization': f"Token {get_token()}"})
    logger.info(f"GET запрос {API_METHODS['tasks']}{task_number}/ - {r.status_code}")
    return r


def get_workers_number(worker_number):
    r = requests.get(url=f"{API_BASE_URL}{API_METHODS['worker_detail']}{worker_number}",
                     headers={'Authorization': f"Token {get_token()}"})
    logger.info(f"GET запрос {API_METHODS['workers']}{worker_number} - {r.status_code}")
    print(r)
    return r


def get_worker_f_chat_id(author_code):
    r = requests.get(url=f"{API_BASE_URL}{API_METHODS['workers_f']}?chat_id={author_code}",
                     headers={'Authorization': f"Token {get_token()}"})
    logger.info(f"GET запрос {API_METHODS['workers_f']}?chat_id={author_code} - {r.status_code}")
    return r


def get_trades_tasks_list(trade_id):

    worker_req = get_worker_f_chat_id(trade_id)
    if len(worker_req.json()) > 0:
        if worker_req.status_code == 200:
            logger.info(f"Результат GET запрос метод worker_f/ с аргументами chat_id={trade_id} - статус - "
                        f"{worker_req.status_code}")
        else:
            logger.warning(f"Результат GET запрос метод worker_f/ с аргументами chat_id={trade_id} - статус - "
                           f"{worker_req.status_code}")
        logger.info(f"GET запрос метод tasks_f/ с аргументами worker={worker_req.json()[0]['code']}&status=Новая")

        r = requests.get(url=f"{API_BASE_URL}tasks_f/?worker={worker_req.json()[0]['code']}&status=Новая",
                         headers={'Authorization': f"Token {get_token()}"})

        if r.status_code == 200:
            logger.info(f"Результат GET запрос метод tasks_f/ с аргументами worker={worker_req.json()[0]['code']}"
                        f"&status=Новая - статус - {r.status_code}")
        else:
            logger.warning(f"Результат GET запрос метод tasks_f/ с аргументами worker={worker_req.json()[0]['code']}"
                           f"&status=Новая - статус - {r.status_code}")
        return {'status': True, 'text': r.json()}
    else:
        return {'status': False, 'text': "Вы не зарегистрированы в системе"}


def get_task_detail(number):
    logger.info("GET запрос метод all-tasks")
    r = requests.get(url=f"{API_BASE_URL}all-tasks/{number}/", headers={'Authorization': f"Token {get_token()}"})
    if r.status_code == 200:
        logger.info(f"Результат GET запроса метод all-tasks - {r.status_code}")
    else:
        logger.warning(f"Результат GET запроса метод all-tasks - {r.status_code}")
    return r.json()


def post_dont_task(number, comment_id):

    t = get_task_number(number)
    if t.status_code == 200:
        task = t.json()
        task['status'] = "Отклонена"
        task['edited'] = True
        task['worker_comment'] = comment_id
        logger.info(f"Создана задача {task}")
        r = requests.put(url=f"{API_BASE_URL}tasks/", data=task, headers={'Authorization': f"Token {get_token()}"})
        logger.info(f"PUT запрос метод tasks/ - data={task}")
        if r.status_code == 201:
            logger.info(f"PUT запрос метод tasks/ - {r.status_code}")
            return {'status': True, 'text': f"{r.status_code}"}
        else:
            logger.warning(f"PUT запрос метод tasks/ - {r.status_code}")
            return {'status': False, 'text': f"{r.status_code}"}
    else:
        logger.warning(f"GET запрос метод tasks/{number}/ - {t.status_code}")


def post_forward_task(number, comment_id, new_worker, author):

    t = get_task_number(number)

    if t.status_code == 200:
        task = t.json()
        logger.info(f"Результат запроса метод tasks/{number}/ - {task} - {t.status_code}")
        new_author = get_worker_f_chat_id(author).json()
        task['status'] = "Переадресована"
        task['edited'] = True
        task['author_comment'] = int(comment_id)
        task['worker'] = str(new_worker)
        task['author'] = new_author[0]['code']
        task['worker_comment'] = CONSTANT_COMMENT_ID

        r = requests.put(url=f"{API_BASE_URL}tasks/", data=task, headers={'Authorization': f"Token {get_token()}"})
        if r.status_code == 201:
            logger.info(f"PUT запрос метод tasks/ - data={task}- {r.status_code}")
            return True
        else:
            logger.warning(f"PUT запрос метод tasks/ - data={task}- {r.status_code} - error - {r.json()}")
            return False

    else:
        logger.info(f"GET запрос метод tasks/ - {t.status_code}")
        return False


def post_add_comment(chat_id, comment, method):
    """Функция для добавления нового комментария, возвращает ID созданного комментария"""

    worker = get_worker_f_chat_id(chat_id)

    if worker.status_code == 200:
        logger.info(f"GET запрос worker_f/?chat_id={chat_id} - method={method} - {worker.status_code}")
        if method == "worker":
            data = {
                "comment": comment,
                "worker": worker.json()[0]['code']
            }
            r = requests.post(url=f"{API_BASE_URL}worker_comment/", data=json.dumps(data),
                              headers={'Authorization': f"Token {get_token()}",
                                       "Content-Type": 'application/json'})

            if r.status_code == 201:
                logger.info(f"POST запрос worker_comment/ - data={data} - {r.status_code}")
                return r.json()['id']
            else:
                logger.warning(f"POST запрос worker_comment/ - data={data} - {r.status_code}")
                return False

        elif method == "author":

            data = {
                "comment": comment,
                "author": worker.json()[0]['code']
            }
            r = requests.post(url=f"{API_BASE_URL}author_comment/", data=json.dumps(data),
                              headers={'Authorization': f"Token {get_token()}",
                                       "Content-Type": 'application/json'})
            if r.status_code == 201:
                logger.info(f"POST запрос author_comment/ - data={data} - {r.status_code}")
                return r.json()['id']
            else:
                logger.warning(f"POST запрос author_comment/ - data={data} - {r.status_code}")
                return False

    else:
        logger.warning(f"GET запрос worker_f/?chat_id={chat_id} - {worker.status_code}")
        return False


def put_register(phone: str, chat_id: str):
    """Функция отправки PUT запроса к БД, с присвоением chat_id"""

    clean_phone = phone.strip('+').replace("-", "").replace("(", "").replace(")", "")
    logger.info(f"Получен запрос на регистрацию - номер {phone}, chat_id={chat_id}")
    t = requests.get(url=f"{API_BASE_URL}worker_f/?phone={clean_phone}",
                     headers={'Authorization': f"Token {get_token()}"})
    if t.status_code == 200:
        logger.info(f"GET запрос worker_f/?phone={phone} - data={t.json()}- {t.status_code}")
        worker = t.json()
        if len(worker) <= 0:
            logger.warning(f"Пользователь с номером {phone} не найден в системе")
            return {'status': False,
                    'message': "Данный контакт не существует в системе, обратитесь к своему руководителю"}
        else:
            worker[0]['chat_id'] = chat_id
            logger.info(f"Пользователю {worker} - назначен chat_id={chat_id}")
            data = json.dumps(worker)
            update = requests.put(url=f"{API_BASE_URL}workers/", data=data,
                                  headers={'Authorization': f"Token {get_token()}",
                                           "Content-Type": 'application/json'})
            if update.status_code == 201:
                logger.info(f"PUT запрос workers/ - data={data} - {update.status_code}")
                return {'status': True, 'message': "Регистрация прошла успешно"}
            else:
                logger.warning(f"PUT запрос workers/ - data={data} - {update.status_code}")
                return {'status': False, 'message': "Техническая ошибка. Обратитесь в тех.поддержку"}
    else:
        logger.warning(f"GET запрос worker_f/?phone={phone} - data={t.json()}- {t.status_code}")
        return {'status': False, 'message': "Техническая ошибка. Обратитесь в тех.поддержку"}


def get_forward_supervisor_controller(worker_number: str, author_number: str) -> dict:

    trades_list = get_workers_number(worker_number)
    author_res = get_workers_number(author_number)
    author = author_res.json()[0]
    controller_res = requests.get(url=f"{API_BASE_URL}{API_METHODS['workers_f']}?controller=true",
                                  headers={'Authorization': f"Token {get_token()}"})
    logger.info(f"GET запрос{API_METHODS['workers_f']}?controller=true - {controller_res.status_code}")
    controller = controller_res.json()[0]
    supervisor_id = trades_list.json()[0]['supervisor_id']
    supervisor_res = requests.get(url=f"{API_BASE_URL}{API_METHODS['supervisors']}{supervisor_id}/",
                                  headers={'Authorization': f"Token {get_token()}"})
    logger.info(f"GET запрос {API_METHODS['supervisors']}{supervisor_id}/ - {supervisor_res.status_code}")
    supervisor = supervisor_res.json()
    worker_partner = get_workers_number(trades_list.json()[0]['partner']).json()[0]
    result_list = comparison(author_list=author, controller_list=controller, supervisor_list=supervisor,
                             worker_list=trades_list.json(), partner_list=worker_partner)
    if trades_list.status_code == 200:
        return {'status': True, 'result': result_list}
    else:
        return {'status': False, 'result': result_list}


def get_partner_worker_list(partner):
    r = requests.get(url=f"{API_BASE_URL}{API_METHODS['partner-worker_f']}?partner={partner}",
                     headers={'Authorization': f"Token {get_token()}"})
    logger.info(f"GET запрос {API_METHODS['partner-worker_f']} - {r.status_code}")
    return r.json()


def get_result_list(group):
    r = requests.get(url=f"{API_BASE_URL}{API_METHODS['result-data_f']}?group={group}",
                     headers={'Authorization': f"Token {get_token()}"})
    logger.info(f"GET запрос {API_METHODS['result-data_f']}  - 'group='{group} - {r.status_code}")
    return r.json()


def get_partner_worker(contact_person_id):
    r = requests.get(url=f"{API_BASE_URL}{API_METHODS['partner-worker_f']}?id={contact_person_id}",
                     headers={'Authorization': f"Token {get_token()}"})
    logger.info(f"GET запрос {API_METHODS['partner-worker_f']} - с атрибутами id={contact_person_id}- {r.status_code}")
    return r.json()


def get_result_detail(result_id):
    r = requests.get(url=f"{API_BASE_URL}{API_METHODS['result']}{result_id}/",
                     headers={'Authorization': f"Token {get_token()}"})
    logger.info(f"GET запрос {API_METHODS['result']} - с атрибутами {result_id} - {r.status_code}")
    return r.json()


def get_result_data_detail(result_id):
    r = requests.get(url=f"{API_BASE_URL}{API_METHODS['result-data']}{result_id}/",
                     headers={'Authorization': f"Token {get_token()}"})
    logger.info(f"GET запрос {API_METHODS['result-data']} - с атрибутами {result_id} - {r.status_code}")
    return r.json()


def get_ready_result_task(result, chat_id):

    task = get_task_number(result['task_number']).json()
    worker_comment_id = post_add_comment(chat_id=chat_id, comment=result['worker_comment'], method="worker")
    if worker_comment_id:
        logger.info(f"Создан комментарий по id={worker_comment_id}")
        result_item = {
            "type": result['task_type'],
            "result": result['result'],
            "contact_person": result['contact_person'],
            "base": task['base'],
            "task_number": result['task_number']
        }
        if result.get('control_date'):
            logger.info(f"Контрольная дата установлена для результата {result_item} - {task['number']}")
            result_item["control_date"] = result['control_date'].date()
        else:
            logger.info(f"Контрольная дата установлена для результата {result_item} - {task['number']}")
            result_item["control_date"] = None

        result_re = requests.post(url=f"{API_BASE_URL}{API_METHODS['result']}", data=result_item,
                                  headers={'Authorization': f"Token {get_token()}"})

        if result_re.status_code == 201:
            logger.info(f"POST запрос {API_METHODS['result']} с data={result_item} - "
                        f"{result_re.status_code}")
            result_id = result_re.json()['id']
            task['edited'] = True,
            task['status'] = "Выполнено",
            task['worker_comment'] = worker_comment_id
            task['result'] = result_id
            add_ready_task = requests.put(url=f"{API_BASE_URL}{API_METHODS['tasks']}", data=task,
                                          headers={'Authorization': f"Token {get_token()}"})
            if add_ready_task.status_code == 201:
                logger.info(f"PUT запрос {API_METHODS['tasks']} c data={task} - "
                            f"{add_ready_task.status_code}")
                return {"status": True, 'text': f"Задача {task['name']} выполнена"}
            else:
                logger.warning(f"PUT запрос {API_METHODS['tasks']} c data={task} - "
                               f"{add_ready_task.status_code}")
                return {"status": False, 'text': f"Статус {add_ready_task.status_code}"}

    else:
        logger.warning(f"Комментарий не создан {task['number']}")
        return {"status": False, 'text': "Комментарий не создан"}


if __name__ == '__main__':
    pass
