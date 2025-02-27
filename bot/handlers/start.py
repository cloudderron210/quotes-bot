from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database import crud


router = Router()
@router.message(Command(commands=['menu', 'start']))
async def menu(msg: Message, session: AsyncSession):
    user_id = msg.chat.id
    username = msg.chat.username
    try: 
        new_user = await crud.insert_new_user(user_id, username, session)
        await msg.answer('New user added!')
    except Exception as e:
        await msg.answer(f'{e}')
