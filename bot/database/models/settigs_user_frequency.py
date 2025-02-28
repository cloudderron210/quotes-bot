from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bot.database.models import Base





class SettingUserFrequency(Base):
    __tablename__ = 'settings_user_frequency'
    
    
    
