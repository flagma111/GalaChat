import sqlite3
from os import getcwd

directory = getcwd()
sql_base_directory = directory + '\\base.db'
sql_conn = sqlite3.connect(sql_base_directory,check_same_thread=False)
sql_cur = sql_conn.cursor()

def create_users_table():

    try:
        sql_cur.execute('DROP TABLE users')
    except:
        pass
    
    sql_script = '''CREATE TABLE users (
    user VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50),
    password VARCHAR(50) );''' 
    
    sql_cur.execute(sql_script)
    sql_conn.commit() 

def find_user(user):
    global sql_cur

    sql_cur.execute('select user,name,password from users where user = "{}"'.format(user))
    return sql_cur.fetchone()

def add_user(IP,name,pwd):
    sql_cur.execute('insert into users(user) values ("{}")'.format(IP))
    print('user added - ',IP)
    sql_conn.commit()
    
def check_new_IP(addres):
    if find_user(addres) == None:
        return False
    else:
        return True

def authorization(IP,pwd):
    global sql_cur

    sql_cur.execute('select password from users where user = "{}" and password ="{}"'.format(IP,pwd))
    return sql_cur.fetchone() != None
 
def get_all_users():
    sql_cur.execute('select * from users')
    for user in sql_cur:
        print(user)

def clear_users():
    sql_cur.execute('delete from users')



