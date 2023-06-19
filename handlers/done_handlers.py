import asyncio
import logging

from aiogram import Router
from aiogram.filters import Text, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram3_calendar import simple_cal_callback
from keyboards.calendar import MySimpleCalendar

from database.database import get_task_detail, get_partner_worker_list, get_result_list, get_partner_worker, \
    get_result_data_detail, get_ready_result_task
from keyboards.trades_keyboards import create_types_done_inline_kb, create_result_types_done_inline_kb, \
    create_contact_person_done_inline_kb

from lexicon import lexicon
from forms.user_form import DoneTaskForm
from services.utils import clear_date
from config_data.config import DELETE_MESSAGE_TIMER

logger = logging.getLogger(__name__)

router: Router = Router()


@router.message(StateFilter(DoneTaskForm.worker_comment))
async def add_ok_task_comment(message: Message, state: FSMContext):
    """Добавление комментария к выполненной задаче"""

    await state.update_data(worker_comment=message.text)
    task = await state.get_data()
    logger.info(f"Комментарий к задаче {task['task_number']} - {message.from_user.id} - "
                f"{message.from_user.username}")
    task_data = await state.get_data()
    res = get_ready_result_task(task_data, message.from_user.id)
    if res['status']:
        logger.info(f"{res['text']}- {message.from_user.id} - {message.from_user.username}")
    else:
        logger.warning(f"{res['text']}- {message.from_user.id} - {message.from_user.username}")
    await state.clear()
    logger.info(f"Cостояние очищено по задаче {task['task_number']} - "
                f"{message.from_user.id} - {message.from_user.username}")
    await message.answer(text=res['text'])


@router.callback_query(Text(startswith='ok'), StateFilter(default_state))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    """При нажатии на кнопку 'Выполнено'"""

    task_number = callback.data.split("_")[1]
    logger.info(f"Получен положительный ответ к задаче {task_number} для {callback.from_user.username}-"
                f"{callback.from_user.id}")
    await state.update_data(task_number=task_number)
    await state.set_state(DoneTaskForm.task_number)
    logger.info(f"Записаны данные в state {await state.get_data()}")
    task = get_task_detail(task_number)
    date = clear_date(task['date'])

    text = f"""
         Укажите какое действие было сделано к задаче от {date}\n\n"{task['name']}"\n
     """
    await callback.message.answer(text=text, reply_markup=create_types_done_inline_kb(1, lexicon.TYPES))
    logger.info(f"Создана клавиатура c 'contacts'")
    await asyncio.sleep(DELETE_MESSAGE_TIMER)
    await callback.message.delete()
    logger.info(f"Сообщение_ok по задаче {task['name']} удалено")


@router.callback_query(Text(text=[f"contact_{x}" for x in lexicon.TYPES.keys()]))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    """При нажатии на клавиатуру действий"""

    task_type = callback.data.split('_')[1]
    await state.update_data(task_type=task_type)
    await state.set_state(DoneTaskForm.task_type)
    task_number = await state.get_data()
    logger.info(f"Получены тип контакта - {task_type} - к задаче {task_number['task_number']}")
    logger.info(f"Записаны данные в state {await state.get_data()}")
    task = get_task_detail(task_number['task_number'])

    text = f"""
            Выберите контактное лицо\n\n
            """

    await callback.message.answer(text=text,
                                  reply_markup=create_contact_person_done_inline_kb(1, get_partner_worker_list(
                                      task['partner']['code'])))
    await asyncio.sleep(DELETE_MESSAGE_TIMER)
    await callback.message.delete()
    logger.info(f"Сообщение_contact по задаче {task_number['task_number']} удалено")


@router.callback_query(Text(startswith="person"))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    person_id = callback.data.split('_')[1]
    partner_worker = get_partner_worker(person_id)
    await state.update_data(contact_person=partner_worker[0]['name'])
    task_number = await state.get_data()
    task = get_task_detail(task_number['task_number'])
    logger.info(f"Получены контактное лицо - {partner_worker[0]['name']} - к задаче {task['name']}")
    logger.info(f"Записаны данные в state {await state.get_data()}")
    date = clear_date(task['date'])

    text = f"""
            Выберите результат действия к задаче {task['name']} от {date}\n\n
            """

    await callback.message.answer(
        text=text,
        reply_markup=create_result_types_done_inline_kb(1, get_result_list(task['base']['group'])))
    await asyncio.sleep(DELETE_MESSAGE_TIMER)
    await callback.message.delete()
    logger.info(f"Сообщение_person по задаче {task_number['task_number']} удалено")


@router.callback_query(Text(startswith="result"))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    result_id = callback.data.split('_')[1]
    result_data = get_result_data_detail(result_id)
    await state.update_data(result=result_data['name'])
    task = await state.get_data()
    tasks_data = get_task_detail(task['task_number'])
    logger.info(f"Получен результат - {result_data['name']} - к задаче {task['task_number']} - "
                f"{callback.message.from_user.id} - "
                f"{callback.message.from_user.username}")
    logger.info(f"Записаны данные в state {await state.get_data()} - "
                f"{callback.message.from_user.id} - "
                f"{callback.from_user.username}")

    if result_data['control_data']:

        text = """
            Установите контрольную дату:
        """

        await callback.message.answer(
            text=text,
            reply_markup=await MySimpleCalendar().start_calendar())
        logger.info(f"Открыта клавиатура для задачи {task['task_number']}")
        await asyncio.sleep(DELETE_MESSAGE_TIMER)
        await callback.message.delete()
        logger.info(f"Сообщение_result по задаче {task['task_number']} удалено")

    else:
        await callback.message.answer(text=f"Укажите комментарий к задаче {tasks_data['name']}")
        await state.set_state(DoneTaskForm.worker_comment)
        await asyncio.sleep(DELETE_MESSAGE_TIMER)
        await callback.message.delete()
        logger.info(f"Сообщение_result по задаче {task['task_number']} удалено")


@router.callback_query(simple_cal_callback.filter())
async def process_simple_calendar(callback: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await MySimpleCalendar().my_process_selection(callback, callback_data)
    logger.info(f"Установлена дата {date}  - {callback.message.from_user.id} - "
                f"{callback.message.from_user.username}")
    if selected:
        await state.update_data(control_date=date)
        task = await state.get_data()
        tasks_data = get_task_detail(task['task_number'])
        await callback.message.answer(text=f"Укажите комментарий к задаче {tasks_data['name']}")
        await state.set_state(DoneTaskForm.worker_comment)
        await asyncio.sleep(DELETE_MESSAGE_TIMER)
        await callback.message.delete()
        logger.info(f"Календарь по задаче {task['task_number']} удален")
