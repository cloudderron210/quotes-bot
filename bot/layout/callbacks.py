from aiogram.filters.callback_data import CallbackData


class AuthorCallback(CallbackData, prefix='au'):
    author:str 
    author_id: int
    
   
