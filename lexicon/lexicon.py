LEXICON: dict[str, str] = {
    'forward': '>>',
    'backward': '<<',
    '/start': '<b>Привет!</b>\n\nЭто бот, в котором '
              'тебе будут приходить задачи из 1С '
              'Чтобы посмотреть список доступных команд - '
              'набери /help',
    '/help': 'Доступные команды:\n\n/register - '
             'пройти процесс регистрации\n/help - '
             'справка по работе бота\n'
             '/tasks - список новых задач',
    '/tasks': '<b>Это список новых задач:</b>',
    '/reset': '<b>Перезагрузить состояние</b>',
    }

LEXICON_COMMANDS: dict[str, str] = {
    '/register': 'Регистрация',
    '/help': 'Справка по работе бота',
    '/tasks': 'Список новых задач',
    '/reset': 'Перезагрузить состояние',
}
LEXICON_ALL_TASKS: dict[str, str] = {
}

TYPES = {
    'email': "Электронное письмо",
    'phone': "Телефонный звонок",
    'meet': "Личная встреча",
    'e-market': "Электронная торговая площадка",
    'postmail': "Почтовое письмо",
    'other': "Прочее"
}