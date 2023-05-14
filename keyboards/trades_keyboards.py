from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database.database import get_trades_list, get_trades_tasks_list, get_forward_trade

from lexicon.lexicon import LEXICON

# [InlineKeyboardButton(text='but_1', url=None, callback_data='but_1', web_app=None, login_url=None,
# switch_inline_query=None, switch_inline_query_current_chat=None, callback_game=None, pay=None)]


def create_trades_register_inline_kb():

    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    contact_btn: KeyboardButton = KeyboardButton(
        text='Передать телефон',
        request_contact=True)

    kb_builder.add(contact_btn)

    keyboard: ReplyKeyboardMarkup = kb_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True)

    return keyboard


def create_new_tasks_inline_kb(task):

    done_button: InlineKeyboardButton = InlineKeyboardButton(
        text="Выполнена ✅",
        callback_data=f"done_{task['number']}")
    not_done_button: InlineKeyboardButton = InlineKeyboardButton(
        text="Не выполнена ❌",
        callback_data=f"dont_{task['number']}")
    forward_button: InlineKeyboardButton = InlineKeyboardButton(
        text="Переадресовать ↪",
        callback_data=f"first_forward_{task['number']}")
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[done_button], [not_done_button], [forward_button]])

    return keyboard


def create_trades_forward_inline_kb(width: int, lst: list) -> InlineKeyboardMarkup:

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []

    if lst:
        for button in range(len(lst)):
            buttons.append(InlineKeyboardButton(
                text=lst[button]['name'],
                callback_data=f"second_forward_{lst[button]['code']}"))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()


if __name__ == '__main__':
    # print(create_trades_tasks_inline_kb(1, get_forward_trade('00000000001')['result']))
    print(get_forward_trade("00000000001"))
    # print(create_trades_forward_inline_kb(1, get_forward_trade("00000000002")['result']))
