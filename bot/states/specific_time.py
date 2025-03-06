from aiogram.fsm.state import State, StatesGroup


class Specifictime(StatesGroup):
    enter_time = State()
    set_time = State()
