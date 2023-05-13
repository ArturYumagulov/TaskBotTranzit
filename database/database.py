import requests

user_dict_template: dict = {'page': 1,
                            'bookmarks': set()}

# Инициализируем "базу данных"
users_db: dict = {}

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


if __name__ == '__main__':
    print(get_trades_tasks_list('239289123'))
