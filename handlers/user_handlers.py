from copy import deepcopy
import asyncio
from aiogram import Router, Dispatcher
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardMarkup, ContentType
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database.database import user_dict_template, users_db, get_trades_list, get_trades_tasks_list, get_author, \
    get_base, get_task_detail, post_add_comment, post_dont_task, put_register
from filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from bot import main

from keyboards.bookmarks_kb import (create_bookmarks_keyboard,
                                    create_edit_keyboard)
from keyboards.trades_keyboards import create_trades_inline_kb
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON
from services.file_handling import book

router: Router = Router()


class Form(StatesGroup):
    comment = State()
    task = State()
    comment_id = State()


# Этот хэндлер будет срабатывать на команду "/start" -
# добавлять пользователя в базу данных, если его там еще не было
# и отправлять ему приветственное сообщение
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(LEXICON[message.text])
    if message.from_user.id not in users_db:
        users_db[message.from_user.id] = deepcopy(user_dict_template)


# Этот хэндлер будет срабатывать на команду "/help"
# и отправлять пользователю сообщение со списком доступных команд в боте
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text])


@router.message(Command(commands='register'))
async def process_register_command(message: Message, ):
    # Инициализируем билдер
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    # Создаем кнопки
    contact_btn: KeyboardButton = KeyboardButton(
        text='Предать телефон',
        request_contact=True)

    # Добавляем кнопки в билдер
    kb_builder.add(contact_btn)

    # Создаем объект клавиатуры
    keyboard: ReplyKeyboardMarkup = kb_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True)

    await message.answer(
        text='Для регистрации необходимо нажать кнопку "Передать телефон"',
        reply_markup=keyboard)
    await message.delete()


@router.message(Command(commands='tasks'))
async def process_beginning_command(message: Message):

    tasks_list = get_trades_tasks_list(message.from_user.id)
    if len(tasks_list) > 0:

        for task in tasks_list:

            date = task['date'].replace("T", " ").replace("Z", "")
            author = get_author(task['author'])
            base = get_base(task['base'])

            done_button: InlineKeyboardButton = InlineKeyboardButton(
                text="Выполнена ✅",
                callback_data=f"done_{task['number']}")
            not_done_button: InlineKeyboardButton = InlineKeyboardButton(
                text="Не выполнена ❌",
                callback_data=f"dont_{task['number']}")
            forward_button: InlineKeyboardButton = InlineKeyboardButton(
                text="Переадресовать ↪",
                callback_data=f"forward_{task['number']}")
            keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
                inline_keyboard=[[done_button], [not_done_button], [forward_button]])

            text = f"""
            Задача номер {task['number']} от {date}\n\n"{task['name']}"\n\nАвтор: { author['name'] }\nОснование: {base['name']}
            """
            await message.answer(
                    text=text,
                    reply_markup=keyboard)
    else:
        await message.answer(text="У вас нет новых задач")


@router.callback_query(Text(startswith='forward'))
async def process_forward_press(callback: CallbackQuery):

    task_number = callback.data.split("_")[1]
    task = get_task_detail(task_number)
    date = task['date'].replace("T", " ").replace("Z", "")
    trades_data = [i['name'] for i in get_trades_list()]

    text = f"""
        Переадресовать задачу №{task['number']} от {date}\n\n"{task['name']}"\n\n на
    """

    await callback.message.edit_text(
        text=text,
        reply_markup=create_trades_inline_kb(1, trades_data))
    await callback.answer()


@router.message(StateFilter(Form.comment))
async def add_comment(message: Message, state: FSMContext):
    comment_id = post_add_comment(chat_id=message.chat.id, comment=message.text)
    await state.update_data(comment=message.text)
    await state.update_data(comment_id=comment_id)
    data = await state.get_data()
    if post_dont_task(number=data['task'], comment_id=data['comment_id']):
        await state.clear()
        await message.answer(f"Задача №{data['task']} сохранена")
    else:
        await message.answer(f"Произошла ошибка, позвоните в техподдержку")


@router.callback_query(Text(startswith='dont'), StateFilter(default_state))
async def process_done_press(callback: CallbackQuery, state: FSMContext):
    task_number = callback.data.split("_")[1]
    await state.update_data(task=task_number)
    task = get_task_detail(task_number)
    date = task['date'].replace("T", " ").replace("Z", "")

    text = f"""
        Укажите комментарий к задаче №{task['number']} от {date}\n\n"{task['name']}"\n
    """
    await callback.message.answer(text=text)
    await state.set_state(Form.comment)
    await asyncio.sleep(3)
    await callback.message.delete()


@router.callback_query(Text(startswith='done'))
async def process_done_press(callback: CallbackQuery):

    task_number = callback.data.split("_")[1]
    task = get_task_detail(task_number)
    date = task['date'].replace("T", " ").replace("Z", "")
    trades_data = [i['name'] for i in get_trades_list()]

    text = f"""
        Переадресовать задачу №{task['number']} от {date}\n\n"{task['name']}"\n\n на
    """

    await callback.message.edit_text(
        text=text,
        reply_markup=create_trades_inline_kb(1, trades_data))
    await callback.answer("Ok")


@router.message()
async def get_contact(message: ContentType.CONTACT):

    phone = message.contact.phone_number
    chat_id = message.contact.user_id
    message.delete()
    response = put_register(phone=phone, chat_id=chat_id)
    if response['status']:
        return await message.answer(text=response['message'])
    else:
        return await message.answer(text=response['message'])
