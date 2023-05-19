from copy import deepcopy
import asyncio
from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message, ContentType, ReplyKeyboardRemove
from database.database import user_dict_template, users_db, get_trades_list, get_trades_tasks_list, get_author, \
    get_base, get_task_detail, post_add_comment, post_dont_task, put_register, post_forward_task, \
    get_partner_worker_list, get_result_list, get_partner_worker, get_result_detail, get_result_data_detail, \
    get_ready_result_task, get_forward_supervisor_controller
from filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import F

from keyboards.trades_keyboards import create_trades_register_inline_kb, \
    create_new_tasks_inline_kb, create_trades_forward_inline_kb, create_types_done_inline_kb, \
    create_result_types_done_inline_kb, create_contact_person_done_inline_kb
from lexicon import lexicon
from lexicon.lexicon import LEXICON
from forms.user_form import Form, ForwardTaskForm, DoneTaskForm
from services.utils import clear_date
from environs import Env
from aiogram3_calendar import simple_cal_callback, SimpleCalendar

env = Env()
env.read_env()

router: Router = Router()
bot = Bot(token=env('BOT_TOKEN'))


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
    date = clear_date(task)

    text = f"""
        Переадресовать задачу №{task['number']} от {date}\n\n"{task['name']}"\n\nАвтор: { author['name'] }\nОснование: {base['name']}
    """

    trades_data = get_forward_supervisor_controller(task['worker'])

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
    date = clear_date(task)

    text = f"""
         Укажите комментарий к задаче №{task['number']} от {date}\n\n"{task['name']}"\n
     """
    await callback.message.answer(text=text)
    await state.set_state(ForwardTaskForm.comment)
    await asyncio.sleep(10)
    await callback.message.delete()


@router.message(StateFilter(Form.comment))
async def add_dont_comment(message: Message, state: FSMContext):
    comment_id = post_add_comment(chat_id=message.chat.id, comment=message.text, method='worker')
    await state.update_data(comment=message.text)
    await state.update_data(comment_id=comment_id)
    data = await state.get_data()
    if post_dont_task(number=data['task'], comment_id=data['comment_id']):
        await state.clear()
        await message.answer(f"Задача №{data['task']} не выполнена")
    else:
        await message.answer(f"Произошла ошибка, позвоните в тех.поддержку")


@router.message(StateFilter(ForwardTaskForm.comment))
async def add_forward_comment(message: Message, state: FSMContext):
    comment_id = post_add_comment(chat_id=message.chat.id, comment=message.text, method='author')
    await state.update_data(comment=message.text)
    await state.update_data(comment_id=comment_id)
    data = await state.get_data()

    if post_forward_task(number=data['task_number'], comment_id=data['comment_id'], new_worker=data['next_user_id'],
                         author=message.from_user.id):
        await state.clear()
        await message.answer(f"Задача №{data['task_number']} переадресована")
    else:
        await message.answer(f"Произошла ошибка, позвоните в тех.поддержку")


@router.message(StateFilter(DoneTaskForm.worker_comment))
async def add_ok_task_comment(message: Message, state: FSMContext):
    await state.update_data(worker_comment=message.text)
    task_data = await state.get_data()

    res = get_ready_result_task(task_data, message.from_user.id)
    await state.clear()
    await message.answer(text=res['text'])


@router.callback_query(Text(startswith='dont'), StateFilter(default_state))
async def process_dont_press(callback: CallbackQuery, state: FSMContext):
    task_number = callback.data.split("_")[1]
    await state.update_data(task=task_number)
    task = get_task_detail(task_number)
    date = clear_date(task)

    text = f"""
        Укажите комментарий к задаче №{task['number']} от {date}\n\n"{task['name']}"\n
    """
    await callback.message.answer(text=text)
    await state.set_state(Form.comment)
    await asyncio.sleep(3)
    await callback.message.delete()


@router.callback_query(Text(startswith='ok'), StateFilter(default_state))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):

    task_number = callback.data.split("_")[1]
    await state.update_data(task_number=task_number)
    await state.set_state(DoneTaskForm.task_number)
    task = get_task_detail(task_number)
    date = clear_date(task)

    text = f"""
         Укажите какое действие было сделано к задаче №{task['number']} от {date}\n\n"{task['name']}"\n
     """
    await callback.message.answer(text=text, reply_markup=create_types_done_inline_kb(1, lexicon.TYPES))

    await asyncio.sleep(10)
    await callback.message.delete()


# don`t Task handler type
@router.callback_query(Text(text=[f"contact_{x}" for x in lexicon.TYPES.keys()]))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    task_type = callback.data.split('_')[1]
    await state.update_data(task_type=task_type)
    await state.set_state(DoneTaskForm.task_type)
    task_number = await state.get_data()
    task = get_task_detail(task_number['task_number'])

    text = f"""
            Выберите контактное лицо\n\n
            """

    await callback.message.answer(text=text,
                                  reply_markup=create_contact_person_done_inline_kb(1, get_partner_worker_list(
                                      task['partner'])))
    await asyncio.sleep(10)
    await callback.message.delete()


@router.callback_query(Text(startswith="person"))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    person_id = callback.data.split('_')[1]
    partner_worker = get_partner_worker(person_id)
    await state.update_data(contact_person=partner_worker[0]['name'])
    task_number = await state.get_data()
    task = get_task_detail(task_number['task_number'])
    date = clear_date(task)

    text = f"""
            Выберите результат действия к задаче №{task['number']} от {date}\n\n
            """

    await callback.message.answer(text=text, reply_markup=create_result_types_done_inline_kb(1, get_result_list(1)))
    await asyncio.sleep(10)
    await callback.message.delete()


@router.callback_query(Text(startswith="result"))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    result_id = callback.data.split('_')[1]
    result_data = get_result_data_detail(result_id)
    await state.update_data(result=result_data['name'])

    if result_data['control_data']:

        text = """
            Установите контрольную дату:
        """

        await callback.message.answer(
            text=text,
            reply_markup=await SimpleCalendar().start_calendar())

    else:
        await callback.message.answer(text="Укажите комментарий")
        await state.set_state(DoneTaskForm.worker_comment)


@router.callback_query(simple_cal_callback.filter())
async def process_simple_calendar(callback: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        await state.update_data(control_date=date)
        await callback.message.answer(text="Укажите комментарий")
        await state.set_state(DoneTaskForm.worker_comment)


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
