
from aiogram.fsm.state import State, StatesGroup


class FrequencyState(StatesGroup):
    seconds = State()
    minutes = State()
    hours = State()
