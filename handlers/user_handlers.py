from copy import deepcopy

from aiogram import Router
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message
from database.database import user_dict_template, users_db, get_trades_list, get_trades_tasks_list, get_author, get_base
from filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
from keyboards.bookmarks_kb import (create_bookmarks_keyboard,
                                    create_edit_keyboard)
from keyboards.trades_keyboards import create_trades_inline_kb
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON
from services.file_handling import book

router: Router = Router()


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


# Этот хэндлер будет срабатывать на команду "/beginning"
# и отправлять пользователю первую страницу книги с кнопками пагинации
@router.message(Command(commands='beginning'))
async def process_beginning_command(message: Message):
    users_db[message.from_user.id]['page'] = 1
    text = book[users_db[message.from_user.id]['page']]
    await message.answer(
            text=text,
            reply_markup=create_pagination_keyboard(
                    'backward',
                    f'{users_db[message.from_user.id]["page"]}/{len(book)}',
                    'forward'))


@router.message(Command(commands='register'))
async def process_beginning_command(message: Message):
    print(message.from_user.id)
    trades_data = [i['name'] for i in get_trades_list()]
    await message.answer(
            text="Выберите нужного сотрудника",
            reply_markup=create_trades_inline_kb(1, trades_data))


@router.message(Command(commands='tasks'))
async def process_beginning_command(message: Message):
    print(message.from_user.id)
    tasks_list = get_trades_tasks_list(message.from_user.id)
    for task in tasks_list:

        date = task['date'].replace("T", " ").replace("Z", "")
        author = get_author(task['author'])
        base = get_base(task['base'])

        text = f"""
        Задача номер {task['number']} от {date}\n\n"{task['name']}"\n\nАвтор: { author['name'] }\nОснование: 
        {base['name']}
        """
        await message.answer(
                text=text,
                reply_markup=create_trades_inline_kb(1, [x['number'] for x in tasks_list]))


@router.callback_query(Text(text='forward'))
async def process_forward_press(callback: CallbackQuery):
    trades_data = [i['name'] for i in get_trades_list()]
    await callback.message.edit_text(
        text="Переадресовать задачу на",
        reply_markup=create_trades_inline_kb(1, trades_data))
    await callback.answer()



# Этот хэндлер будет срабатывать на команду "/continue"
# и отправлять пользователю страницу книги, на которой пользователь
# остановился в процессе взаимодействия с ботом
# @router.message(Command(commands='continue'))
# async def process_continue_command(message: Message):
#     text = book[users_db[message.from_user.id]['page']]
#     await message.answer(
#                 text=text,
#                 reply_markup=create_pagination_keyboard(
#                     'backward',
#                     f'{users_db[message.from_user.id]["page"]}/{len(book)}',
#                     'forward'))


# Этот хэндлер будет срабатывать на команду "/bookmarks"
# и отправлять пользователю список сохраненных закладок,
# если они есть или сообщение о том, что закладок нет
# @router.message(Command(commands='bookmarks'))
# async def process_bookmarks_command(message: Message):
#     if users_db[message.from_user.id]["bookmarks"]:
#         await message.answer(
#             text=LEXICON[message.text],
#             reply_markup=create_bookmarks_keyboard(
#                 *users_db[message.from_user.id]["bookmarks"]))
#     else:
#         await message.answer(text=LEXICON['no_bookmarks'])


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
# во время взаимодействия пользователя с сообщением-книгой
# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
# во время взаимодействия пользователя с сообщением-книгой
# @router.callback_query(Text(text='backward'))
# async def process_backward_press(callback: CallbackQuery):
#     if users_db[callback.from_user.id]['page'] > 1:
#         users_db[callback.from_user.id]['page'] -= 1
#         text = book[users_db[callback.from_user.id]['page']]
#         await callback.message.edit_text(
#                 text=text,
#                 reply_markup=create_pagination_keyboard(
#                     'backward',
#                     f'{users_db[callback.from_user.id]["page"]}/{len(book)}',
#                     'forward'))
#     await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с номером текущей страницы и добавлять текущую страницу в закладки
# @router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit())
# async def process_page_press(callback: CallbackQuery):
#     users_db[callback.from_user.id]['bookmarks'].add(
#         users_db[callback.from_user.id]['page'])
#     await callback.answer('Страница добавлена в закладки!')


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок
# @router.callback_query(IsDigitCallbackData())
# async def process_bookmark_press(callback: CallbackQuery):
#     text = book[int(callback.data)]
#     users_db[callback.from_user.id]['page'] = int(callback.data)
#     await callback.message.edit_text(
#                 text=text,
#                 reply_markup=create_pagination_keyboard(
#                     'backward',
#                     f'{users_db[callback.from_user.id]["page"]}/{len(book)}',
#                     'forward'))
#     await callback.answer()
# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "отменить" во время работы со списком закладок (просмотр и редактирование)
# @router.callback_query(Text(text='cancel'))
# async def process_cancel_press(callback: CallbackQuery):
#     await callback.message.edit_text(text=LEXICON['cancel_text'])
#     await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок к удалению
# @router.callback_query(IsDelBookmarkCallbackData())
# async def process_del_bookmark_press(callback: CallbackQuery):
#     users_db[callback.from_user.id]['bookmarks'].remove(
#                                                     int(callback.data[:-3]))
#     if users_db[callback.from_user.id]['bookmarks']:
#         await callback.message.edit_text(
#                     text=LEXICON['/bookmarks'],
#                     reply_markup=create_edit_keyboard(
#                             *users_db[callback.from_user.id]["bookmarks"]))
#     else:
#         await callback.message.edit_text(text=LEXICON['no_bookmarks'])
#     await callback.answer()


