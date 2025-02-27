from typing import Callable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from bot.database.session_helper import db_helper
    




    

class DatabaseMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable, event: TelegramObject, data: dict):
        async for session in db_helper.get_session():
            data["session"] = session
            return await handler(event, data)



            
