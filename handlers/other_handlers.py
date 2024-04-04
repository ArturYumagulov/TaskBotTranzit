import logging

from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ContentType, ReplyKeyboardRemove

from config_data.config import TASK_GROUP
from database.database import get_trades_tasks_list, put_register
from keyboards.trades_keyboards import create_trades_register_inline_kb, create_new_tasks_inline_kb, \
    create_new_tasks_inline_kb_census
from lexicon.lexicon import LEXICON
from services.utils import clear_date, del_ready_task, update_task_message_id

logger = logging.getLogger(__name__)

router: Router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    logger.info(f"Поступила команда старт - {message.from_user.id} - {message.from_user.username}")
    await message.answer(LEXICON[message.text])


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    logger.info(f"Поступила команда help - {message.from_user.id} - {message.from_user.username}")
    await message.answer(LEXICON[message.text])


@router.message(Command(commands='register'))
async def process_register_command(message: Message, ):
    logger.info(f"Поступила команда регистрации - {message.from_user.id} - {message.from_user.username}")
    await message.answer(
        text='Для регистрации необходимо нажать кнопку "Передать телефон"',
        reply_markup=create_trades_register_inline_kb())


@router.message(Command(commands='tasks'))
async def all_tasks_command(message: Message):

    # TODO добавить функционал удаления старых задач, после вывода новых

    tasks_list = await get_trades_tasks_list(message.from_user.id)

    # [del_ready_task(message.from_user.id, x['message_id']) for x in tasks_list['text']]  # Удаление плашек выгруженных задач

    logger.info(f"Поступила команда tasks - {message.from_user.id} - {message.from_user.username}")
    if tasks_list['status']:
        if len(tasks_list['text']) > 0:

            for task in tasks_list['text']:

                group_name = task['base']['group']
                date = clear_date(task['date'])
                deadline = clear_date(task['deadline'])

                if group_name == '000000004':  # Если "Разработка контрагента"

                    author_comment = task['author_comment']['comment'].split('_')[0]

                    text = f"Задача от " \
                           f"{date}\n\n" \
                           f"Сенсус по адресу: '{task['name']}'\n\n" \
                           f"<b>Исполнить до:</b>\n" \
                           f"{deadline}\n" \
                           f"<b>Автор:</b>\n" \
                           f"{task['author']['name']}\n" \
                           f"<b>Контрагент:</b>\n" \
                           f"{task['partner']['name']}\n" \
                           f"<b>Основание:</b>\n" \
                           f"{task['base']['name']}\n" \
                           f"<b>Комментарий автора:</b>\n" \
                           f"{author_comment}"

                    await message.answer(
                        text=text,
                        reply_markup=create_new_tasks_inline_kb_census(task))

                else:
                    text = f"Задача от " \
                           f"{date}\n\n" \
                           f"'{TASK_GROUP[group_name]}'\n\n" \
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

                    await message.answer(
                            text=text,
                            reply_markup=create_new_tasks_inline_kb(task))

        else:
            await message.answer(text="У вас нет новых задач")
    else:
        await message.answer(text=tasks_list['text'])


@router.message(F.content_type.in_({ContentType.CONTACT}))
async def get_contact(message: ContentType.CONTACT):

    phone = message.contact.phone_number
    chat_id = message.contact.user_id
    message.delete()
    response = await put_register(phone=phone, chat_id=chat_id)
    logger.info(f"Передан номер телефона - {phone} - {message.from_user.id} - {message.from_user.username}")
    if response['status']:
        return await message.reply(text=response['message'], reply_markup=ReplyKeyboardRemove())
    else:
        return await message.reply(text=response['message'], reply_markup=ReplyKeyboardRemove())


# Этот хэндлер будет реагировать на любые сообщения пользователя,
# не предусмотренные логикой работы бота
@router.message()
async def send_echo(message: Message):
    await message.answer(LEXICON['/help'])
