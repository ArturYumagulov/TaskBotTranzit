LEXICON: dict[str, str] = {
    'forward': '>>',
    'backward': '<<',
    '/start': '<b>Привет, читатель!</b>\n\nЭто бот, в котором '
              'тебе будут приходить задачи из 1С '
              'Чтобы посмотреть список доступных команд - '
              'набери /help',
    '/help': '<b>Это бот</b>\n\nДоступные команды:\n\n/register - '
             'пройти процесс регистрации\n/help - '
             'справка по работе бота\n',
    '/tasks': '<b>Это список ваших задач:</b>',
    }

LEXICON_COMMANDS: dict[str, str] = {
    '/register': 'Регистрация',
    '/help': 'Справка по работе бота',
    '/tasks': 'Задачи'
}