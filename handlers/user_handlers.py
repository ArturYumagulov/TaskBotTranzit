from copy import deepcopy
import asyncio
from aiogram import Router
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message, ContentType, ReplyKeyboardRemove
from database.database import user_dict_template, users_db, get_trades_list, get_trades_tasks_list, get_author, \
    get_base, get_task_detail, post_add_comment, post_dont_task, put_register, get_forward_trade, post_forward_task
from filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import F

from keyboards.bookmarks_kb import (create_bookmarks_keyboard,
                                    create_edit_keyboard)
from keyboards.trades_keyboards import create_trades_register_inline_kb, \
    create_new_tasks_inline_kb, create_trades_forward_inline_kb
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON
from forms.user_form import Form, ForwardTaskForm

router: Router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(LEXICON[message.text])
    if message.from_user.id not in users_db:
        users_db[message.from_user.id] = deepcopy(user_dict_template)


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text])


@router.message(Command(commands='register'))
async def process_register_command(message: Message, ):
    await message.answer(
        text='Для регистрации необходимо нажать кнопку "Передать телефон"',
        reply_markup=create_trades_register_inline_kb())


@router.message(Command(commands='tasks'))
async def process_beginning_command(message: Message):

    tasks_list = get_trades_tasks_list(message.from_user.id)

    if len(tasks_list) > 0:

        for task in tasks_list:

            date = task['date'].replace("T", " ").replace("Z", "")
            author = get_author(task['author'])
            base = get_base(task['base'])
            text = f"""
            Задача номер {task['number']} от {date}\n\n"{task['name']}"\n\nАвтор: { author['name'] }\nОснование: {base['name']}
            """
            await message.answer(
                    text=text,
                    reply_markup=create_new_tasks_inline_kb(task))
    else:
        await message.answer(text="У вас нет новых задач")


@router.callback_query(Text(startswith='first_forward'), StateFilter(default_state))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    task_number = callback.data.split("_")[2]
    await state.update_data(task_number=task_number)
    task = get_task_detail(task_number)
    author = get_author(task['author'])
    base = get_base(task['base'])
    date = task['date'].replace("T", " ").replace("Z", "")

    text = f"""
        Переадресовать задачу №{task['number']} от {date}\n\n"{task['name']}"\n\nАвтор: { author['name'] }\nОснование: {base['name']}
    """
    trades_data = get_forward_trade(task['worker'])
    if trades_data['status']:
        await callback.message.edit_text(
            text=text,
            reply_markup=create_trades_forward_inline_kb(1, trades_data['result']))

    await asyncio.sleep(10)
    await callback.message.delete()


@router.callback_query(Text(startswith='second_forward'), StateFilter(default_state))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):

    author_number = callback.data.split("_")[2]
    await state.update_data(next_user_id=author_number)
    data = await state.get_data()
    task = get_task_detail(data['task_number'])

    date = task['date'].replace("T", " ").replace("Z", "")

    text = f"""
         Укажите комментарий к задаче №{task['number']} от {date}\n\n"{task['name']}"\n
     """
    await callback.message.answer(text=text)
    await state.set_state(ForwardTaskForm.comment)


@router.message(StateFilter(Form.comment))
async def add_dont_comment(message: Message, state: FSMContext):
    comment_id = post_add_comment(chat_id=message.chat.id, comment=message.text, method='worker')
    await state.update_data(comment=message.text)
    await state.update_data(comment_id=comment_id)
    data = await state.get_data()
    if post_dont_task(number=data['task'], comment_id=data['comment_id']):
        await state.clear()
        await message.answer(f"Задача №{data['task']} сохранена")
    else:
        await message.answer(f"Произошла ошибка, позвоните в техподдержку")


@router.message(StateFilter(ForwardTaskForm.comment))
async def add_forward_comment(message: Message, state: FSMContext):
    comment_id = post_add_comment(chat_id=message.chat.id, comment=message.text, method='author')
    await state.update_data(comment=message.text)
    await state.update_data(comment_id=comment_id)
    data = await state.get_data()
    if post_forward_task(number=data['task_number'], comment_id=data['comment_id'], new_worker=data['next_user_id'],
                         author=message.from_user.id):
        await state.clear()
        await message.answer(f"Задача №{data['task_number']} сохранена")
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


@router.message(F.content_type.in_({ContentType.CONTACT}))
async def get_contact(message: ContentType.CONTACT):

    phone = message.contact.phone_number
    chat_id = message.contact.user_id
    message.delete()
    response = put_register(phone=phone, chat_id=chat_id)
    if response['status']:
        return await message.reply(text=response['message'], reply_markup=ReplyKeyboardRemove())
    else:
        return await message.reply(text=response['message'], reply_markup=ReplyKeyboardRemove())
