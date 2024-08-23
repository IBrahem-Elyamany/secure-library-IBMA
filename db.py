import utils


def connect_to_database(name='database.db'):
    import sqlite3
    return sqlite3.connect(name, check_same_thread=False)


def init_db(connection):
    cursor = connection.cursor()

    cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL UNIQUE,
            email TEXT UNIQUE,
			password TEXT NOT NULL,
            fName TEXT ,
            lName TEXT,
            photo_name TEXT
		)
	''')

    connection.commit()


def add_user(connection, username, email, lName, password , photo_name):
    cursor = connection.cursor()
    # hashed_password = utils.hash_password(password)
    query = '''INSERT INTO users (username ,email ,fName ,lName , password , photo_name) VALUES (? ,? ,? ,? ,? ,? )'''
    cursor.execute(query, (username ,email ,username ,lName , password , photo_name))
    connection.commit()


def get_all_users(connection):
    cursor = connection.cursor()
    query = 'SELECT * FROM users'
    cursor.execute(query)
    return cursor.fetchall()


def seed_admin_user(connection):
    admin_username = 'admin'
    admin_password = 'admin'

    # Check if admin user exists
    admin_user = get_user(connection, admin_username)
    if not admin_user:
        add_user(connection, admin_username, 'admin@gmail.com', 'admin', admin_password , 'images.png')
        print("Admin user seeded successfully.")


def search_users(connection, search_query):
    cursor = connection.cursor()
    query = '''SELECT username FROM users WHERE username LIKE ?'''
    cursor.execute(query, (f"%{search_query}%",))
    return cursor.fetchall()

def delete_user(connection, username):
    cursor = connection.cursor()
    query = ''' DELETE FROM users WHERE username = ? '''
    cursor.execute(query, (username,)) 
    connection.commit()

def update_user(connection , user_data):
    cursor = connection.cursor()
    query = ''' UPDATE users set fname = ? , lName = ? , creditCard = ? WHERE username = ? '''
    cursor.execute(query,(user_data['fname'] , user_data['lname'] , user_data['card'] , user_data['username']))
    connection.commit() 


def update_photo(connection, filename , username):
    cursor = connection.cursor()  
    query = '''UPDATE users SET photo_name = ? WHERE username = ?'''
    cursor.execute(query, (filename,username))  
    connection.commit()  


def get_user(connection, username):
    cursor = connection.cursor()
    query = '''SELECT * FROM users WHERE username = ?'''
    cursor.execute(query, (username,))
    return cursor.fetchone()



def inittable_product(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prodects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amout INTEGER NOT NULL,
            price INTEGER NOT NULL,
            photo TEXT,
            text TEXT,
            type TEXT
        )
    ''')
    conn.commit()

def add_product(conn,data):
    cur=conn.cursor()
    quary="INSERT INTO prodects(name,price,amout,photo,text,type) VALUES (?,?,?,?,?,?)"
    cur.execute(quary,(data['name'],data['price'],data['amout'],data['photo'],data['text'],data['type']))
    conn.commit()

def get_product(conn):
    cur=conn.cursor()
    quary="SELECT * FROM prodects"
    cur.execute(quary)
    return cur.fetchall()

def delete_product(conn,id):
    cur=conn.cursor()
    quary="DELETE FROM prodects WHERE id=?"
    cur.execute(quary,(id,))
    conn.commit()
