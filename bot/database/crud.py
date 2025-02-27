from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.session_helper import db_helper
from bot.database.models import User

async def insert_new_user(user_id, username, session: AsyncSession):
    new_user = User(user_id=user_id, username=username)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
