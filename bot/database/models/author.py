from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models import Base

if TYPE_CHECKING:
    from bot.database.models import User, Quote

class Author(Base):
    __tablename__ = 'authors'

    name: Mapped[str] = mapped_column(unique=True)
    def_: Mapped[bool] = mapped_column(name='def', default=False)
    
    users: Mapped[list['User']] = relationship(secondary='user_author', back_populates='authors')
    default_users: Mapped[list['User']] = relationship('User', back_populates='def_author')
    quotes: Mapped[list["Quote"]] = relationship("Quote", back_populates="author")
    
