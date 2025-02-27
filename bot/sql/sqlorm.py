from sqlalchemy import TIMESTAMP, BigInteger, create_engine, Column, Integer, String, ForeignKey, func, Text, Boolean, desc, delete
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql.expression import func
from bot.sql.models import User, Author, Quote, UserAuthor, SettingsDefaultAuthor, FrequencyMode, SettingsUserFrequency, MisqcellaneousQuote
import logging

logging.basicConfig(level=logging.DEBUG)  # Set logging level
logger = logging.getLogger(__name__)

Base = declarative_base()

engine = create_engine(
    'mysql+mysqlconnector://derron:Cloudderron210!@194.120.116.89/telegram',
    pool_size=5,
    poolclass=QueuePool
)

Session = sessionmaker(bind=engine)

def get_default_author_2(user_id):
    session = Session()
    try:
        # user = session.query(User).filter_by(user_id=user_id).first()
        # sda = session.query(SettingsDefaultAuthor).filter_by(user_id = user.id).first()
        # author = session.query(Author).filter_by(id=sda.author_id).first()
        # return author.author

        user = session.query(User).filter_by(user_id=user_id).first()
        def_author = user.settings_default_author[0] 
        # print(f'{def_author}')
        logger.debug(f'Default author: {user.settings_default_author}')
        logger.debug(f'Default author: {user.settings_default_author[0]}')
        logger.debug(f'Default author.author: {def_author.author}')

        return def_author.author.author
        
        # sql='''
        #     SELECT a.author
        #     FROM users u
        #     JOIN settings_default_author sda ON u.id = sda.user_id
        #     JOIN authors a on sda.author_id = a.id
        #     WHERE u.user_id = %s 
        # '''
        # cursor.execute(sql,[user_id])
        # result = cursor.fetchone()[0]
        # return(result)
            
    except Exception as e:
        session.rollback()
        raise Exception(f'{e}')
    finally:
        session.close

def add_quote_2(user_id, quote):
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
        return new_quote.quote
    except Exception as e:
        session.rollback()
        raise Exception(e)
    finally:
        session.close()
    

def add_misc_quote_2(author, quote, user_id):
    session = Session()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            new_misc_quote = MisqcellaneousQuote(author=author, quote=quote, added_by=user.id )
            session.add(new_misc_quote)
            session.commit()
            return user.id
        else:
            return 'No user found'
    except Exception as e:
        session.rollback()
        raise Exception(e)
    finally:
        session.close()
    
    

def get_random_message_2(user_id, mixed=False):
    session = Session()
    try:
        if mixed == False:
            setting_author = (
                session.query(SettingsDefaultAuthor)
                .join(User, User.id == SettingsDefaultAuthor.user_id)
                .filter(User.user_id == user_id)
                .first()
            )

            get_quote = (
                session.query(Quote)
                .filter(Quote.author_id == setting_author.author_id) # type:ignore
                .order_by(func.rand())
                .first()
                
            )
            return get_quote.quote # type:ignore
        else:
            get_quote = (
                session.query(Quote.quote, Author.author)
                .join(Author, Author.id == Quote.author_id)
                .join(UserAuthor, UserAuthor.author_id == Quote.author_id)
                .join(User, User.id == UserAuthor.user_id)
                .filter(User.user_id == user_id)
            )            
            get_misc = (
                session.query(MisqcellaneousQuote.quote, MisqcellaneousQuote.author)
                .join(User, User.id == MisqcellaneousQuote.added_by)
                .filter(User.user_id == user_id)
            )
            result = get_quote.union(get_misc).order_by(func.rand()).first()
            return result
    except Exception as e:
        session.rollback()
        raise Exception(e)
    finally:
        session.close()






def insert_new_user_2(user_id, username):
    session = Session()
    try:
        new_user = User(user_id=user_id, username=username)
        session.add(new_user)
        session.commit()
        return 'newuserino'
    except Exception as e:
        raise Exception(e)
    finally:
        session.close()
        

def check_default_author_2(user_id):
    session = Session()
    try:
        result = (
            session.query(SettingsDefaultAuthor)
            .join(User, User.id == SettingsDefaultAuthor.user_id)
            .filter(User.user_id == user_id)
            .count()
        ) 
        return result 
    except Exception as e:
        raise Exception(e)
    finally:
        session.close()


def set_default_author_2(user_id, author):
    session = Session()
    try:
        # user = (
        #     session.query(User)
        #     .filter(User.user_id == user_id)
        #     .first()
        # )
        user = User(user_id=user_id)
        
        (session.query(SettingsDefaultAuthor)
        .filter(SettingsDefaultAuthor.user_id == user.id)
        .delete())


        author = (
            session.query(Author)
            .filter(Author.author == author)
        )

        if user and author:
            new_default_author = SettingsDefaultAuthor(user_id=user.id, author_id=author.id)
            session.add(new_default_author)
            session.commit()
        
        
    except Exception as e:
        raise Exception(e)
    finally:
        session.close()

            # sql = '''
            #     INSERT INTO settings_default_author(user_id, author_id)
            #     SELECT u.id, a.id
            #     FROM users u
            #     JOIN authors a
            #     WHERE u.user_id = %s AND a.author = %s
            # '''
            #
    





    
    


    
    
    

    



    

