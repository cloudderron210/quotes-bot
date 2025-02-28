from sqlalchemy import Result, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from bot.database.models import Author, User, Quote

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

async def get_current_defualt_author(user_id: int, session: AsyncSession) -> Author:
    stmt = select(User).options(selectinload(User.def_author)).where(User.user_id == user_id)
    result: Result = await session.execute(stmt)
    user = result.scalar()
    return user.def_author

async def get_all_quotes_of_author(author: Author, session: AsyncSession):
    stmt = select(Author).options(selectinload(Author.quotes)).where(Author.id == author.id)
    result: Result = await session.execute(stmt)
    authorr = result.scalar()
    if authorr:
        return authorr.quotes
    

async def add_quote(author: Author, session: AsyncSession, text: str) -> Quote:
    new_quote = Quote(author=author, quote_text=text)
    
    session.add(new_quote)
    await session.commit()
    await session.refresh(new_quote)
    return new_quote
    
async def get_random_quote(user_id: int, session: AsyncSession) -> str:
    stmt = (
        select(User)
        .options(
            joinedload(User.def_author).
                joinedload(Author.quotes)
        )
        .where(User.user_id == user_id)
    )
    user = await session.scalar(stmt)
    
    stmt =(
        select(Quote.quote_text)
        .join(Author, Author.id == Quote.author_id)
        .join(User, User.default_author == Author.id)
        .where(User.user_id == user_id)
        .order_by(func.random())
        .limit(1)
    )

    result = await session.scalar(stmt)
    if result:
        return result
    else:
        return('')
    
    # stmt = (
    #     select(User)
    #     .options(selectinload(User.def_author), selectinload(Author.quotes))
    #     .where(User.user_id == user_id)
    # )
    # user = await session.scalar(stmt)
    # if user:
    #     return [quote.quote_text for quote in user.def_author.quotes]
    # else:
    #     return []
            

    
    
    
    
