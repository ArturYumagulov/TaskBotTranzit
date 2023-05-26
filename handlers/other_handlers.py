import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ContentType, ReplyKeyboardRemove

from database.database import get_trades_tasks_list, put_register
from keyboards.trades_keyboards import create_trades_register_inline_kb, create_new_tasks_inline_kb
from lexicon.lexicon import LEXICON
from services.utils import clear_date

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
async def new_tasks_command(message: Message):

    tasks_list = get_trades_tasks_list(message.from_user.id)

    logger.info(f"Поступила команда tasks - {message.from_user.id} - {message.from_user.username}")
    if tasks_list['status']:
        if len(tasks_list['text']) > 0:
            for task in tasks_list['text']:
                date = clear_date(task)
                text = f"""
                Задача номер {str(task['number'])}\nот {date}\n\n"{task['name']}"\n\n<b>Автор:</b>\n{task['author']['name']}\n<b>Основание:</b>\n{task['base']['name']}\n<b>Комментарий автора:</b>\n{task['author_comment']['comment']}
                """

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
    response = put_register(phone=phone, chat_id=chat_id)
    logger.info(f"Передан номер телефона - {phone} - {message.from_user.id} - {message.from_user.username}")
    if response['status']:
        return await message.reply(text=response['message'], reply_markup=ReplyKeyboardRemove())
    else:
        return await message.reply(text=response['message'], reply_markup=ReplyKeyboardRemove())


# # Этот хэндлер будет реагировать на любые сообщения пользователя,
# # не предусмотренные логикой работы бота
# @router.message()
# async def send_echo(message: Message):
#     await message.answer(LEXICON['/help'])
