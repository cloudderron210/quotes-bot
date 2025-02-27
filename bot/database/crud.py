from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import Author, User
from bot.database.session_helper import db_helper

async def insert_new_user(user_id, username, session: AsyncSession) -> User:
    new_user = User(user_id=user_id, username=username)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

async def inser_new_author(name: str, session: AsyncSession) -> Author:
    new_author = Author(name=name)
    session.add(new_author)
    await session.commit()
    await session.refresh(new_author)
    return new_author

async def set_default_author_for_new(user: User, session: AsyncSession):
    stmt = update(User).where(User.id == user.id).values(default_author = 2)
    await session.execute(stmt)
    await session.commit()

