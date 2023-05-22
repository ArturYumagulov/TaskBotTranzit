import datetime
import json
import requests

BASE_URL = "http://192.168.80.224:8000/api/v1/"


def get_trades_list():
    r = requests.get(url=f'{BASE_URL}workers/')
    return r.json()


def get_trades_tasks_list(trade_id):
    worker_req = requests.get(url=f"{BASE_URL}worker_f/?chat_id={trade_id}")
    r = requests.get(url=f"{BASE_URL}tasks_f/?worker={worker_req.json()[0]['code']}&status=Новая")
    return r.json()


def get_author(author_code):
    r = requests.get(url=f"{BASE_URL}workers/{author_code}/")
    return r.json()


def get_base(number):
    r = requests.get(url=f"{BASE_URL}base/{number}/")
    return r.json()


def get_task_detail(number):
    r = requests.get(url=f"{BASE_URL}all-tasks/{number}/")
    return r.json()


def post_dont_task(number, comment_id):

    task = requests.get(url=f"{BASE_URL}tasks/{number}/").json()
    task['status'] = "Не выполнено"
    task['edited'] = True
    task['worker_comment'] = comment_id
    r = requests.put(url=f"{BASE_URL}tasks/", data=task)
    if r.status_code == 201:
        return True
    else:
        return False


def post_forward_task(number, comment_id, new_worker, author):

    task = requests.get(url=f"{BASE_URL}tasks/{number}/").json()

    new_author = get_worker(author)
    task['status'] = "Переадресована"
    task['edited'] = True
    task['author_comment'] = int(comment_id)
    task['worker'] = str(new_worker)
    task['author'] = new_author[0]['code']
    task['worker_comment'] = 1

    r = requests.put(url=f"{BASE_URL}tasks/", data=task)

    if r.status_code == 201:
        return True
    else:
        return False


def post_add_comment(chat_id, comment, method):

    worker = requests.get(url=f"{BASE_URL}worker_f/?chat_id={chat_id}")

    if method == "worker":

        data = {
            "comment": comment,
            "worker": worker.json()[0]['code']
        }

        r = requests.post(url=f"{BASE_URL}worker_comment/", data=data)
        return r.json()['id']

    elif method == "author":

        data = {
            "comment": comment,
            "author": worker.json()[0]['code']
        }
        r = requests.post(url=f"{BASE_URL}author_comment/", data=data)
        return r.json()['id']
    else:
        return False


def put_register(phone: str, chat_id: str):

    clean_phone = phone.strip('+').replace("-", "").replace("(", "").replace(")", "")

    worker = requests.get(url=f"{BASE_URL}worker_f/?phone={clean_phone}").json()

    if len(worker) <= 0:
        return {'status': False, 'message': "Данный контакт не существует в системе, обратитесь к своему руководителю"}
    else:
        worker[0]['chat_id'] = chat_id

        data = json.dumps(worker)

        update = requests.put(url=f"{BASE_URL}workers/", data=data, headers={'Content-Type': 'application/json'})

        if update.status_code == 201:
            return {'status': True, 'message': "Регистрация прошла успешно"}
        else:
            return {'status': False, 'message': "Техническая ошибка. Обратитесь в тех.поддержку"}


def get_forward_supervisor_controller(number: str) -> dict:

    result = []
    trades_list = requests.get(url=f"{BASE_URL}workers/{number}/")
    controller = requests.get(url=f"{BASE_URL}worker_f/?controller=true")
    supervisor_id = trades_list.json()['supervisor']
    supervisor = requests.get(url=f"{BASE_URL}supervisors/{supervisor_id}/")
    result.append(supervisor.json())
    result.append(controller.json()[0])

    if trades_list.status_code == 200:
        return {'status': True, 'result': result}
    else:
        return {'status': False, 'result': result}


def get_worker(author_code):
    r = requests.get(url=f"{BASE_URL}worker_f/?chat_id={author_code}")
    return r.json()


def get_partner_worker_list(partner):
    r = requests.get(url=f"{BASE_URL}partner-worker_f/?partner={partner}")
    return r.json()


def get_result_list(group):
    r = requests.get(url=f"{BASE_URL}result-data_f/?group={group}")
    return r.json()


def get_partner_worker(contact_person_id):
    r = requests.get(url=f"{BASE_URL}partner-worker_f/?id={contact_person_id}")
    return r.json()


def get_result_detail(result_id):
    r = requests.get(url=f"{BASE_URL}result/{result_id}/")
    return r.json()


def get_result_data_detail(result_id):
    r = requests.get(url=f"{BASE_URL}result-data/{result_id}/")
    return r.json()


def get_ready_result_task(result, chat_id):

    task = requests.get(url=f"{BASE_URL}tasks/{result['task_number']}/").json()

    new_worker_comment = {
        "comment": result['worker_comment'],
        "worker": task['worker']
    }
    add_new_comment = requests.post(url=f"{BASE_URL}worker_comment/", data=new_worker_comment)
    worker_comment_id = add_new_comment.json()['id']
    if add_new_comment.status_code == 201:
        result_item = {
            "type": result['task_type'],
            "result": result['result'],
            "contact_person": result['contact_person'],
            "base": task['base'],
            "group": 1,
            "task_number": result['task_number']
        }
        if result.get('control_date'):
            result_item["control_date"] = result['control_date'].date()
        else:
            result_item["control_date"] = None

        result_re = requests.post(url=f"{BASE_URL}result/", data=result_item)

        if result_re.status_code == 201:
            result_id = result_re.json()['id']
            task['edited'] = True,
            task['status'] = "Выполнено",
            task['worker_comment'] = worker_comment_id
            task['result'] = result_id
            add_ready_task = requests.put(url=f"{BASE_URL}tasks/", data=task)

            if add_ready_task.status_code == 201:
                return {"status": True, 'text': f"Задача {task['number']} выполнена"}
            else:
                return {"status": False, 'text': f"Статус {add_ready_task.status_code}"}

    else:
        return {"status": False, 'text': "Worker не создан"}


if __name__ == '__main__':
    # print(get_trades_tasks_list('239289123'))
    # print(post_dont_task("00000000001"))
    # print(put_register("+7(9872609314", "239289123"))
    # print(put_register("+7(9991571663", "239289123"))
    # print(get_forward_trade("00000000001"))
    # print(post_add_comment(chat_id="239289123", comment="Test", method="author"))
    # print(get_worker("239289123"))
    # print(post_forward_task(number="00000000013", new_worker="00000000001", author="239289123", comment_id=13))
    # print(get_result_list(1))
    # print(get_result_detail(1))
    # get_task_detail("00000000013")
    # print(get_forward_supervisor_controller("00000000001")['result'])
    result = {'task_number': '00000000023', 'task_type': 'other', 'contact_person': 'Пупкин Вася_2', 'result': 'ОБЕЩАНИЕ ОПЛАТИТЬ', 'control_date': datetime.datetime(2023, 5, 25, 0, 0), 'worker_comment': 'Комм'}
    print(get_ready_result_task(result=result, chat_id=239289123))
