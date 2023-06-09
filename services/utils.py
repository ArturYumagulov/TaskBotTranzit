def clear_date(data):
    """Функция очистки даты от символов"""
    return data.replace("T", " ").replace("Z", "")


def comparison(controller_list, supervisor_list, author_list):
    """Функция сравнения, для вывода нужных адресатов для переадресации задачи"""

    result_list = []

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
