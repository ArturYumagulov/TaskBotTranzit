from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database.database import get_forward_supervisor_controller


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
        callback_data=f"ok_{task['number']}")
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


def create_types_done_inline_kb(width: int, dct: dict) -> InlineKeyboardMarkup:

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []

    if dct:
        for button in dct:
            buttons.append(InlineKeyboardButton(
                text=dct[button],
                callback_data=f"contact_{button}"))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()


def create_result_types_done_inline_kb(width: int, dct: dict) -> InlineKeyboardMarkup:

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []

    if dct:
        for button in dct:
            buttons.append(InlineKeyboardButton(
                text=button['name'],
                callback_data=f"result_{button['id']}"))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()


def create_contact_person_done_inline_kb(width: int, dct: dict):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []

    if dct:
        for button in dct:
            buttons.append(InlineKeyboardButton(
                text=button['name'],
                callback_data=f"person_{button['id']}"))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()


if __name__ == '__main__':
    # print(create_trades_tasks_inline_kb(1, get_forward_trade('00000000001')['result']))
    # print(get_forward_trade("00000000001"))
    print(create_trades_forward_inline_kb(1, get_forward_supervisor_controller("00000000001")['result']))
    # print(create_types_done_inline_kb(1, lexicon.TYPES))
    # print(create_contact_person_done_inline_kb(1, get_partner_worker_list('00000000001')))
    # print(create_result_types_done_inline_kb(1, get_result_list(1)))
