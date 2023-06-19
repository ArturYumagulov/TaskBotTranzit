def clear_date(data):
    """Функция очистки даты от символов"""
    return data.replace("T", " ").replace("Z", "")


def comparison(controller_list, supervisor_list, author_list, partner_list=None):
    """Функция сравнения, для вывода нужных адресатов для переадресации задачи"""

    result_list = []

    if partner_list is not None:
        if author_list['controller']:
            result_list.append(supervisor_list)
            result_list.append(author_list)
            result_list.append(partner_list)
        elif author_list['code'] == supervisor_list['code']:
            result_list.append(controller_list)
            result_list.append(author_list)
            result_list.append(partner_list)
        elif author_list['code'] == partner_list['code']:
            result_list.append(partner_list)
            result_list.append(controller_list)
            result_list.append(supervisor_list)
    else:
        if author_list['controller']:
            result_list.append(supervisor_list)
            result_list.append(author_list)
        elif author_list['code'] == supervisor_list['code']:
            result_list.append(controller_list)
            result_list.append(author_list)
        else:
            result_list.append(controller_list)
            result_list.append(supervisor_list)
            result_list.append(author_list)

    return result_list
