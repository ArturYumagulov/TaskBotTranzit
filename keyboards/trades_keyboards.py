from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.database import get_trades_list, get_trades_tasks_list

from lexicon.lexicon import LEXICON

# [InlineKeyboardButton(text='but_1', url=None, callback_data='but_1', web_app=None, login_url=None,
# switch_inline_query=None, switch_inline_query_current_chat=None, callback_game=None, pay=None)]


def create_trades_inline_kb(width: int,
                     lst: list,
                     **kwargs: str) -> InlineKeyboardMarkup:

    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if lst:
        for button in range(len(lst)):
            buttons.append(InlineKeyboardButton(
                text=lst[button],
                callback_data=lst[button]))

    # if kwargs:
    #     for button, text in kwargs.items():
    #         buttons.append(InlineKeyboardButton(
    #             text=text,
    #             callback_data=button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


def create_trades_tasks_inline_kb(width: int, *args) -> InlineKeyboardMarkup:

    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for i in args:
            print(i)
            # buttons.append(InlineKeyboardButton(
            #     text=lst[button],
            #     callback_data=lst[button]))

    # if kwargs:
    #     for button, text in kwargs.items():
    #         buttons.append(InlineKeyboardButton(
    #             text=text,
    #             callback_data=button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


if __name__ == '__main__':

    # print(buttons)
    print(create_trades_tasks_inline_kb(1, get_trades_tasks_list('239289123')))

