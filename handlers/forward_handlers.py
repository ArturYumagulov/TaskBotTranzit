import asyncio

from aiogram import Router
from aiogram.filters import Text, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.database import get_task_detail, get_forward_supervisor_controller, post_add_comment, post_forward_task
from forms.user_form import ForwardTaskForm
from keyboards.trades_keyboards import create_trades_forward_inline_kb
from services.utils import clear_date

router: Router = Router()


@router.callback_query(Text(startswith='first_forward'), StateFilter(default_state))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    task_number = callback.data.split("_")[2]
    await state.update_data(task_number=task_number)
    task = get_task_detail(task_number)
    date = clear_date(task)

    text = f"""
        Переадресовать задачу №{task['number']} от {date}\n\n"{task['name']}"\n\n<b>Автор:</b> {task['author']['name']}\n<b>Основание:</b> {task['base']['name']}
    """

    trades_data = get_forward_supervisor_controller(task['worker']['code'])

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

