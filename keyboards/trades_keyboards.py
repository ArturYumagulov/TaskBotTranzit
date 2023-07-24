from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from lexicon.lexicon import TASK_KEYS


def create_trades_register_inline_kb():

    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    contact_btn: KeyboardButton = KeyboardButton(
        text=TASK_KEYS['get_phone'],
        request_contact=True)

    kb_builder.add(contact_btn)
    keyboard: ReplyKeyboardMarkup = kb_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True)
    return keyboard


def create_new_tasks_inline_kb(task):

    done_button: InlineKeyboardButton = InlineKeyboardButton(
        text=TASK_KEYS['done']['text'],
        callback_data=f"{TASK_KEYS['done']['callback_data']}{task['number']}")
    # not_done_button: InlineKeyboardButton = InlineKeyboardButton(
    #     text=TASK_KEYS['dont']['text'],
    #     callback_data=f"{TASK_KEYS['dont']['callback_data']}{task['number']}")
    forward_button: InlineKeyboardButton = InlineKeyboardButton(
        text=TASK_KEYS['forward']['text'],
        callback_data=f"{TASK_KEYS['forward']['callback_data']}{task['number']}")
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[done_button], [forward_button]])  # [not_done_button][1]
    return keyboard


def create_trades_forward_inline_kb(width: int, lst: list) -> InlineKeyboardMarkup:

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []
    if lst:
        for button in range(len(lst)):
            if lst[button] is not None:
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
                callback_data=f"result_{button['code']}"))

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
    pass
