from sqlalchemy import Result, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from bot.database.models import Author, User, Quote, UserAuthor


async def inser_new_author(user_id: int,name: str, session: AsyncSession) -> Author:
    new_author = Author(name=name)
    session.add(new_author)

    
    await session.commit()
    await session.refresh(new_author)
    return new_author

async def init_new_user(user_id: int, username: str | None, session: AsyncSession):
    new_user = User(user_id=user_id, username=username)
    session.add(new_user)
    await session.flush()
    await session.refresh(new_user)
    
    stmt = update(User).where(User.id == new_user.id).values(default_author = 2)
    await session.execute(stmt)
    
    new_user_author = UserAuthor(user_id=new_user.id, author_id=2)
    session.add(new_user_author)
    
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
    # stmt = (
    #     select(User)
    #     .options(
    #         joinedload(User.def_author).
    #             joinedload(Author.quotes)
    #     )
    #     .where(User.user_id == user_id)
    # )
    # user = await session.scalar(stmt)
    
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
    
async def get_all_authors_of_user(user_id: int, session: AsyncSession):
    
    stmt = (
        select(User)
        .options(selectinload(User.authors))
        .where(User.user_id == user_id)
    )

    stmt = (
        select(Author.name)
        .join(UserAuthor, UserAuthor.author_id == Author.id)
        .join(User, User.id == UserAuthor.user_id)
        .where()
    )

    user = await session.scalar(stmt)
    if user:
        return user.authors 
    
    
    
