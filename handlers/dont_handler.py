import asyncio

from aiogram import Router
from aiogram.filters import Text, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.database import get_task_detail, post_add_comment, post_dont_task
from services.utils import clear_date

from forms.user_form import Form

router: Router = Router()


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
