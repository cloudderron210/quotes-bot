from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models import Base

if TYPE_CHECKING:
    from bot.database.models import Author

class User(Base):
    __tablename__ = 'users'
    
    user_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(nullable=True)
    default_author: Mapped[int] = mapped_column(ForeignKey('authors.id'), nullable=True)

    authors: Mapped[list['Author']] = relationship(secondary='user_author', back_populates='users')
