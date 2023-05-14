from aiogram.filters.state import State, StatesGroup


class Form(StatesGroup):
    comment = State()
    task = State()
    comment_id = State()


class ForwardTaskForm(StatesGroup):
    comment = State()
    task_number = State()
    next_user_id = State()
