from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models import Base



class Author(Base):
    __tablename__ = 'authors'

    author: Mapped[str] = mapped_column(unique=True)
    def_: Mapped[bool] = mapped_column(name='def', default=False)
    
    # quotes = relationship('Quote', back_populates='author')
    # user_authors = relationship('UserAuthor', back_populates='author')
    # settings_default_author = relationship('SettingsDefaultAuthor', back_populates='author')
