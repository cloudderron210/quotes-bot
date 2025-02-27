

from aiogram.fsm.state import State, StatesGroup


class AuthorState(StatesGroup):
    new_author = State()
    add_quote = State()
    add_misc_quote = State()
    add_quote_author = State()
    set_interval_seconds = State()

