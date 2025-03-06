from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bot.database.models import Base

if TYPE_CHECKING:
    from database.models import Author





class Quote(Base):
    __tablename__ = 'quotes'
    
    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'), nullable=True) 
    quote_text: Mapped[str] = mapped_column(Text)
    date_added: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))

    author: Mapped["Author"] = relationship("Author", back_populates="quotes")
    
