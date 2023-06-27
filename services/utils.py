from config_data import config


def clear_date(data):
    """Функция очистки даты от символов"""
    return data.replace("T", " ").replace("Z", "")


def comparison(controller_list, supervisor_list, author_list, worker_list, partner_list=None):
    """Функция сравнения, для вывода нужных адресатов для переадресации задачи"""

    result_list = []
    if partner_list is not None:
        if author_list['controller'] and partner_list['code'] != supervisor_list['code']:
            result_list.append(supervisor_list)
            result_list.append(author_list)
            result_list.append(partner_list)
        elif author_list['code'] == config.SOFT_COLLECTION_USER_CODE:
            result_list.append(supervisor_list)
            result_list.append(controller_list)
            result_list.append(partner_list)
        elif author_list['code'] == supervisor_list['code'] and supervisor_list['code'] != partner_list['code']:
            result_list.append(controller_list)
            result_list.append(author_list)
            result_list.append(partner_list)
        elif supervisor_list['code'] == partner_list['code']:
            result_list.append(controller_list)
            result_list.append(supervisor_list)
        elif author_list['code'] == partner_list['code']:
            result_list.append(partner_list)
            result_list.append(controller_list)
            result_list.append(supervisor_list)
        elif author_list['code'] == supervisor_list['code']:
            result_list.append(controller_list)
            result_list.append(author_list)
        elif partner_list['code'] == worker_list['code']:
            result_list.append(controller_list)
            result_list.append(author_list)
            result_list.append(supervisor_list)
        else:
            result_list.append(controller_list)
            result_list.append(supervisor_list)
            result_list.append(author_list)
            result_list.append(partner_list)

    else:
        if author_list['controller']:
            result_list.append(supervisor_list)
            result_list.append(author_list)
        elif author_list['code'] == config.SOFT_COLLECTION_USER_CODE:
            result_list.append(supervisor_list)
            result_list.append(controller_list)
        elif author_list['code'] == supervisor_list['code']:
            result_list.append(controller_list)
            result_list.append(author_list)
        elif author_list['code'] == controller_list['code']:
            result_list.append(controller_list)
            result_list.append(supervisor_list)
        else:
            result_list.append(controller_list)
            result_list.append(supervisor_list)
            result_list.append(author_list)

    return result_list


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
