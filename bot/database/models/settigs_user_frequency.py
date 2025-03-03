from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bot.database.models import Base

if TYPE_CHECKING:
    from bot.database.models import User



class SettingUserFrequency(Base):
    __tablename__ = 'settings_user_frequency'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    interval_seconds: Mapped[int] = mapped_column(default=5)
    times_per_day: Mapped[int] = mapped_column(default=20)
    specific_times: Mapped[int] = mapped_column(nullable=True)
    send_at_nighttime: Mapped[bool] = mapped_column(default=True)
    
    user: Mapped['User'] = relationship('User', back_populates='settings')
    
    
    
