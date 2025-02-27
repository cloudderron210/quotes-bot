from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base import Base

class User(Base):
    __tablename__ = 'users'
    
    user_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(nullable=True)


    
