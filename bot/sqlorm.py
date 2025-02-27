from sqlalchemy import TIMESTAMP, BigInteger, create_engine, Column, Integer, String, ForeignKey, func, Text, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.pool import QueuePool


Base = declarative_base()

engine = create_engine(
    'mysql+mysqlconnector://derron:Cloudderron210!@45.82.15.19/telegram',
    pool_size=5,
    poolclass=QueuePool
)


Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True)
    username = Column(String(255), nullable=True)

    user_authors = relationship('UserAuthor', back_populates='user')
    miscellaneous_quotes = relationship('MisqcellaneousQuote', back_populates='user')
    settings_default_author = relationship('SettingsDefaultAuthor', back_populates='user')
    settings_user_frequency = relationship('SettingsUserFrequency', back_populates='user')

class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String(255), unique=True )
    def_ = Column('def', Boolean, default=False)
    
    quotes = relationship('Quote', back_populates='author')
    user_authors = relationship('UserAuthor', back_populates='author')
    settings_default_author = relationship('SettingsDefaultAuthor', back_populates='author')
    
class Quote(Base):
    __tablename__ = 'quotes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=True) 
    quote = Column(Text)
    date = Column(TIMESTAMP, nullable=True)

    author = relationship('Author', back_populates='quotes')

class UserAuthor(Base):
    __tablename__ = 'user_authors'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'), primary_key=True)

    user = relationship('User', back_populates='user_authors')
    author = relationship('Author', back_populates='user_authors')

class SettingsDefaultAuthor(Base):
    __tablename__ = 'settings_default_author'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'))

    user = relationship('User', back_populates='settings_default_author')
    author = relationship('Author', back_populates='settings_default_author')


class SettingsUserFrequency(Base):
    __tablename__ = 'settings_user_frequency'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    frequency_mode_id = Column(Integer, ForeignKey('frequency_modes.id'), nullable=False)
    interval_seconds = Column(Integer, default=5)
    times_per_day = Column(Integer, default=2020)
    specific_times = Column(String(255), nullable=True)
    
    user = relationship('User')
    frequency_mode = relationship('FrequencyMode')

class FrequencyMode(Base):
    __tablename__ = 'frequency_modes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mode_name = Column(String(50), nullable=False)

    
class MisqcellaneousQuote(Base):
    __tablename__ = 'miscellaneous_quotes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    author = Column(String(255), nullable=False)
    quote = Column(Text)
    added_by = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='miscellaneous_quotes')
    author = relationship('Author', back_populates='miscellaneous_quotes')

def add_quote(user_id, quote):
    session = Session()
    try:
        setting_author = (
            session.query(SettingsDefaultAuthor)
            .join(User, User.id == SettingsDefaultAuthor.user_id)
            .filter(User.user_id == user_id)
            .first()
        )
    
        new_quote = Quote(author_id=setting_author.author_id, quote=quote) # type:ignore
        session.add(new_quote)
        session.commit()
        return 'message_stored'
    except Exception as e:
        session.rollback()
        raise Exception(e)
    finally:
        session.close()
    

    





    
    


    
    
    

    



    

