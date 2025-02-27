from datetime import datetime
from sqlalchemy import ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from bot.sqlorm import Base







class Quote(Base):
    __tablename__ = 'quotes'
    
    author_id: Mapped[int]  = mapped_column(ForeignKey('authors.id'), nullable=True) 
    quote: Mapped[Text] 
    date_added: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))

    
