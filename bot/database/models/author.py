from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models import Base

if TYPE_CHECKING:
    from bot.database.models import User

class Author(Base):
    __tablename__ = 'authors'

    author: Mapped[str] = mapped_column(unique=True)
    def_: Mapped[bool] = mapped_column(name='def', default=False)
    
    users: Mapped[list['User']] = relationship(secondary='user_author', back_populates='authors')
