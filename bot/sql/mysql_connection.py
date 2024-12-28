from mysql.connector import pooling

db_pool = pooling.MySQLConnectionPool(
    pool_name='telegram_pool',
    pool_size=5,
    host= '194.120.116.89',
    user='derron',
    password='Cloudderron210!',
    database='telegram'
)

def get_db_connection():
    return db_pool.get_connection()


def add_quote(user_id, quote):
    db = get_db_connection()
    
    try:
        with db.cursor() as cursor:
            sql = '''
                INSERT INTO quotes(author_id, quote)
                SELECT sda.author_id, %s 
                FROM settings_default_author sda
                JOIN users u ON sda.user_id = u.id 
                WHERE u.user_id = %s 
            '''
            cursor.execute(sql,[quote, user_id])
            db.commit()
            return 'message stored'
    except Exception as e:
        raise(Exception(e))
    finally:
        db.close()
        

def get_random_message(user_id, mixed=False, order='rand()', limit=1):
    db = get_db_connection()
    try:
        if mixed:
            with db.cursor() as cursor:
                sql = f'''
                    SELECT q.quote, a.author FROM quotes q
                    JOIN authors a ON q.author_id = a.id
                    JOIN user_authors ua ON q.author_id = ua.author_id
                    JOIN users u ON ua.user_id = u.id
                    WHERE u.user_id = %s 

                    UNION

                    SELECT mq.quote, mq.author FROM miscellaneous_quotes mq
                    JOIN users u ON mq.added_by = u.id
                    WHERE u.user_id = %s

                    ORDER BY {order} LIMIT %s
                '''
                cursor.execute(sql,[user_id, user_id, limit])
                result = cursor.fetchall()
                return result
        else:
            with db.cursor() as cursor:
                sql = f'''
                    SELECT quote FROM quotes q
                    JOIN settings_default_author sda ON q.author_id = sda.author_id
                    JOIN users u ON sda.user_id = u.id
                    WHERE u.user_id = %s
                    ORDER BY {order} LIMIT %s
                    
                '''
                cursor.execute(sql,[user_id, limit])
                result = cursor.fetchall()
                return result
    except Exception as e:
        return f'{e}'
    finally:
        db.close()


def get_all_quotes():
    pass
        
def get_random_author(user_id):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql = '''
                SELECT a.author FROM authors a
                JOIN user_authors ua ON ua.author_id = a.id
                JOIN users u ON ua.user_id = u.id
                WHERE u.user_id = %s AND a.id != 25 
                ORDER BY rand() LIMIT 1
            '''
            cursor.execute(sql,[user_id])
            result = cursor.fetchone()[0]
            return f'{result}'
    except Exception as e:
        return f'{e}'
    finally:
        db.close()
        
def insert_new_user(user_id, username):
    db = get_db_connection()
    
    try:
        with db.cursor() as cursor:
            sql='''
                INSERT IGNORE INTO users (user_id, username)
                VALUES (%s, %s)
            '''
            cursor.execute(sql,[user_id, username])
            db.commit()
            
    except Exception as e:
        return f'{e}'
    finally:
        db.close()
    

def insert_new_author(author):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql='''
                INSERT INTO authors (author)
                VALUES (%s)
            '''
            cursor.execute(sql,[author])
            db.commit()
            
    except Exception as e:
        return f'{e}'
    finally:
        db.close()


def check_default_author(user_id):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql = '''
                select COUNT(*) from settings_default_author sda
                JOIN users u ON sda.user_id = u.id
                WHERE u.user_id = %s 
            '''
            cursor.execute(sql,[user_id])
            result = cursor.fetchone()[0]
            return result
            
    except Exception as e:
        raise Exception(f'{e}, {sql}')
    finally:
        db.close()
    
def set_default_author(user_id, author):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql='''
                DELETE sda FROM settings_default_author sda
                JOIN users u ON sda.user_id = u.id
                WHERE u.user_id = %s;
                
            '''
            cursor.execute(sql,[user_id])
            
            sql = '''
                INSERT INTO settings_default_author(user_id, author_id)
                SELECT u.id, a.id
                FROM users u
                JOIN authors a
                WHERE u.user_id = %s AND a.author = %s
            '''
            cursor.execute(sql,[user_id, author])
            db.commit()
            
    except Exception as e:
        raise Exception(f'{e}, {sql}')
    finally:
        db.close()
    
    
def set_user_authors(user_id, new_author=None):
    db = get_db_connection()
    if new_author != None:
        try:
            with db.cursor() as cursor:
                cursor.execute('START TRANSACTION')
                
                sql='''
                    INSERT INTO authors(author)
                    VALUES (%s);
                '''
                cursor.execute(sql,[new_author])
                
                sql='''
                    INSERT INTO user_authors (user_id, author_id)
                    SELECT u.id, a.id
                    FROM users u
                    JOIN authors a
                    WHERE u.user_id = %s and a.author = (%s)
                '''
                cursor.execute(sql,[user_id, new_author])
                db.commit()
                
        except Exception as e:
            db.rollback()
            db.close()
            raise Exception(f'{e}')
        finally:
            db.close()
    
    else:    
        try:
            with db.cursor() as cursor:
                sql='''
                    INSERT INTO user_authors (user_id, author_id)
                    SELECT u.id, a.id
                    FROM users u
                    JOIN authors a
                    WHERE u.user_id = %s and a.def = TRUE
                '''
                cursor.execute(sql,[user_id])
                db.commit()
                result = cursor.fetchall()
                return(result)
                
        except Exception as e:
            raise Exception(f'{e}')
        finally:
            db.close()
    
def get_all_authors():
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql='''
                SELECT author FROM authors 
            '''
            cursor.execute(sql)
            result = cursor.fetchall()
            return(result)
            
    except Exception as e:
        raise Exception(f'{e}')
    finally:
        db.close()
    
    

def get_authors_list(user_id):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql='''
                SELECT a.author FROM authors a
                JOIN user_authors ua ON a.id = ua.author_id  
                JOIN users u ON u.id = ua.user_id
                WHERE u.user_id = %s AND a.id != 25
            '''
            cursor.execute(sql,[user_id])
            result = cursor.fetchall()
            return(result)
            
    except Exception as e:
        raise Exception(f'{e}')
    finally:
        db.close()

def add_misc_quote(author, quote, user_id):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql='''
                INSERT INTO miscellaneous_quotes (author, quote, added_by)
                SELECT %s, %s, u.id
                FROM users u
                WHERE u.user_id = %s
            '''
            cursor.execute(sql,[str(author), str(quote), int(user_id)])
            db.commit()
            result = cursor.fetchone()
            return result
    except Exception as e:
        raise Exception(f'{e}')
    finally:
        db.close()
    
    

def get_default_author(user_id):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql='''
                SELECT a.author
                FROM users u
                JOIN settings_default_author sda ON u.id = sda.user_id
                JOIN authors a on sda.author_id = a.id
                WHERE u.user_id = %s 
            '''
            cursor.execute(sql,[user_id])
            result = cursor.fetchone()[0]
            return(result)
            
    except Exception as e:
        raise Exception(f'{e}')
    finally:
        db.close()
    
def set_interval_seconds(user_id, seconds):
    db = get_db_connection()
    
    try:
        with db.cursor() as cursor:
            sql='''
                UPDATE setting_user_frequency suf
                JOIN users u ON suf.user_id = u.id
                SET interval_seconds = %s
                WHERE u.user_id = %s 
            '''
            cursor.execute(sql,[int(seconds), user_id])
            db.commit()
            # result = cursor.fetchone()[0]
            # return(result)
            
    except Exception as e:
        raise Exception(f'{e}')
    finally:
        db.close()
    
def get_interval_seconds(user_id):
    db = get_db_connection()
    
    try:
        with db.cursor() as cursor:
            sql='''
                SELECT interval_seconds 
                FROM setting_user_frequency suf
                JOIN users u ON suf.user_id = u.id
                WHERE u.user_id = %s  
            '''
            cursor.execute(sql,[user_id])
            result = cursor.fetchone()[0]
            return(result)
            
    except Exception as e:
        raise Exception(f'{e}')
    finally:
        db.close()


def set_user_frequency(user_id):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql='''
                INSERT INTO setting_user_frequency(user_id, frequency_mode_id)
                SELECT u.id, 1
                FROM users u
                WHERE u.user_id = %s
            '''
            cursor.execute(sql,[user_id])
            db.commit()
            
    except Exception as e:
        raise Exception(f'{e}')
    finally:
        db.close()
    

    



