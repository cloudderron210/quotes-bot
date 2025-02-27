from sqlalchemy import Column, ForeignKey
from bot.database.models import Base


class UserAuthor(Base):
    __tablename__ = 'user_author'
    
    user_id = Column(ForeignKey('users.id'))
    author_id = Column(ForeignKey('authors.id'))
