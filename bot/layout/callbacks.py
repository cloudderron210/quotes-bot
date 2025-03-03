from aiogram.filters.callback_data import CallbackData


class AuthorCallback(CallbackData, prefix='au'):
    author:str 
    author_id: int
    
class UnitsCallback(CallbackData, prefix='un'):
    units: str
    multiplier: int
   
class SpamModeCallback(CallbackData, prefix='sp'):
    name: str
