import enum
from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models import Base

if TYPE_CHECKING:
    from bot.database.models import Author, SettingUserFrequency


class FrequencyEnum(enum.Enum):
    INTERVAL = 'interval'
    TIMES_PER_DAY = 'times_per_day'
    SPECIFIC_TIMES = 'specific_times'

class User(Base):
    __tablename__ = 'users'
    
    user_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(nullable=True)
    default_author: Mapped[int] = mapped_column(ForeignKey('authors.id'), nullable=True)
    frequency_mode: Mapped[str] = mapped_column(Enum(FrequencyEnum), default=FrequencyEnum.INTERVAL)

    authors: Mapped[list['Author']] = relationship(secondary='user_author', back_populates='users')
    def_author: Mapped['Author'] = relationship('Author',back_populates='default_users', lazy='joined')
    settings: Mapped['SettingUserFrequency'] = relationship('SettingUserFrequency', back_populates='user')
    
