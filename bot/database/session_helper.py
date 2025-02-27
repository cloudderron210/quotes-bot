from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, async_scoped_session
from asyncio import current_task
from bot.config import settings


class DataBaseHelper:
    def __init__(self):
        self.engine = create_async_engine(
            url=settings.db_url,
            echo=settings.db_echo
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
            autocommit=False
        )
        
    def get_scoped_session(self): 
        return async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task
        )
    
    async def session_dependency(self) -> AsyncSession:
        session = self.get_scoped_session()
        yield session
        await session.close()


db_helper = DataBaseHelper()
