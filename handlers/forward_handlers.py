import asyncio
import logging

from aiogram import Router
from aiogram.filters import Text, StateFilter, Command
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.database import get_task_detail, get_forward_supervisor_controller, post_add_comment, post_forward_task
from forms.user_form import ForwardTaskForm
from keyboards.trades_keyboards import create_trades_forward_inline_kb
from services.utils import clear_date
from config_data.config import DELETE_MESSAGE_TIMER


logger = logging.getLogger(__name__)

router: Router = Router()


@router.callback_query(Text(startswith='first_forward'), StateFilter(default_state))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    task_number = callback.data.split("_")[2]

    logger.info(f"Получен ответ на переадресацию задачи {task_number} от {callback.message.from_user.id} - "
                f"{callback.from_user.username}")

    await state.update_data(task_number=task_number)

    logger.info(
        f"Записаны данные в state {await state.get_data()} - {callback.from_user.id} - {callback.from_user.username}")

    task = get_task_detail(task_number)
    date = clear_date(task['date'])
    deadline = clear_date(task['deadline'])

    text = f"Переадресовать задачу от " \
           f"{date}\n\n" \
           f"'{task['name']}'\n\n" \
           f"<b>Исполнить до:</b>\n" \
           f"{deadline}\n" \
           f"<b>Автор:</b>\n" \
           f"{task['author']['name']}\n" \
           f"<b>Контрагент:</b>\n" \
           f"{task['partner']['name']}\n" \
           f"<b>Основание:</b>\n" \
           f"{task['base']['name']}\n" \
           f"<b>Комментарий автора:</b>\n" \
           f"{task['author_comment']['comment']}"

    trades_data = get_forward_supervisor_controller(task['worker']['code'], task['author']['code'])
    if trades_data['status']:
        await callback.message.edit_text(
            text=text,
            reply_markup=create_trades_forward_inline_kb(1, trades_data['result']))

    await asyncio.sleep(DELETE_MESSAGE_TIMER)
    await callback.message.delete()
    logger.info(f"Сообщение_first по задаче {task['number']} удалено")


@router.callback_query(Text(startswith='second_forward'), StateFilter(default_state))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    author_number = callback.data.split("_")[2]
    await state.update_data(next_user_id=author_number)
    task = await state.get_data()
    logger.info(f"Получен номер {author_number} адресуемого по задаче {task['task_number']} от "
                f"{callback.message.from_user.id} - "
                f"{callback.from_user.username}")
    data = await state.get_data()
    logger.info(f"Записаны данные {task} от {callback.message.from_user.id} - "
                f"{callback.from_user.username}")
    task = get_task_detail(data['task_number'])
    date = clear_date(task['date'])

    text = f"""
         Укажите комментарий к задаче от {date}\n\n"{task['name']}"\n ⬇️⬇️⬇️
     """
    await callback.message.answer(text=text)
    await state.set_state(ForwardTaskForm.comment)


@router.message(StateFilter(ForwardTaskForm.comment))
async def add_forward_comment(message: Message, state: FSMContext):
    comment_id = post_add_comment(chat_id=message.chat.id, comment=message.text, method='author')
    await state.update_data(comment=message.text)
    await state.update_data(comment_id=comment_id)
    data = await state.get_data()
    logger.info(f"Получен комментарий '{message.text}' к задаче {data['task_number']} - "
                f"{message.from_user.id} - {message.from_user.username}")
    logger.info(f"Записаны в state данные {data} к задаче {data['task_number']} - "
                f"{message.from_user.id} - {message.from_user.username}")
    task = get_task_detail(data['task_number'])
    if post_forward_task(number=data['task_number'], comment_id=data['comment_id'], new_worker=data['next_user_id'],
                         author=message.from_user.id):
        await state.clear()
        logger.info(f"Очищены в state данные к задаче {data['task_number']} - "
                    f"{message.from_user.id} - {message.from_user.username}")
        logger.info(f"Задача {data['task_number']} переадресована - "
                    f"{message.from_user.id} - {message.from_user.username}")
        await message.answer(f"Задача {task['name']} переадресована")
    else:
        await state.clear()
        logger.warning(f"Ошибка в задаче  {task['name']} - "
                       f"{message.from_user.id} - {message.from_user.username}")
        await message.answer(f"Произошла ошибка, позвоните в тех.поддержку")


@router.message(Command(commands='reset'))
async def send_echo(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Система перезагружена")
    logger.info(f"Состояние очищено {message.from_user.id}")

