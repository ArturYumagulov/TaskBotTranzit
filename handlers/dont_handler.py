import asyncio
import logging

from aiogram import Router
from aiogram.filters import Text, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.database import get_task_detail, post_add_comment, post_dont_task
from services.utils import clear_date

from forms.user_form import Form
from config_data.config import DELETE_MESSAGE_TIMER

logger = logging.getLogger(__name__)


router: Router = Router()


@router.message(StateFilter(Form.comment))
async def add_dont_comment(message: Message, state: FSMContext):
    comment_id = post_add_comment(chat_id=message.chat.id, comment=message.text, method='worker')
    await state.update_data(comment=message.text)
    await state.update_data(comment_id=comment_id)
    task = await state.get_data()
    logger.info(f"Комментарий к задаче {task['task']} - {message.from_user.id} - "
                f"{message.from_user.username}")
    data = await state.get_data()
    res = post_dont_task(number=data['task'], comment_id=data['comment_id'])
    if res['status']:
        await state.clear()
        await message.answer(f"Задача №{data['task']} не выполнена")
        logger.info(f"Результат задачи {data['task']} успешно сохранен - {res['text']} - "
                    f"{message.from_user.id} - {message.from_user.username}")
    else:
        await message.answer(f"Произошла ошибка, позвоните в тех.поддержку")
        logger.info(f"Результат задачи {data['task']} не сохранено- {res['text']}"
                    f"{message.from_user.id} - {message.from_user.username}")


@router.callback_query(Text(startswith='dont'), StateFilter(default_state))
async def process_dont_press(callback: CallbackQuery, state: FSMContext):
    task_number = callback.data.split("_")[1]
    logger.info(f"Получен отрицательный ответ к задаче {task_number} для {callback.from_user.id} - {callback.from_user.username}")
    await state.update_data(task=task_number)
    task = get_task_detail(task_number)
    logger.info(f"Записаны данные в state {await state.get_data()} - {callback.from_user.id} - {callback.from_user.username}")

    date = clear_date(task)

    text = f"""
        Укажите комментарий к задаче №{task['number']} от {date}\n\n"{task['name']}"\n
    """
    await callback.message.answer(text=text)
    await state.set_state(Form.comment)
    await asyncio.sleep(DELETE_MESSAGE_TIMER)
    await callback.message.delete()
    logger.info(f"Сообщение_ok по задаче {task['number']} удалено")
