import utils
import check


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
            photo_name TEXT,
            wallet INTEGER
		)
	''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amout INTEGER NOT NULL,
            price INTEGER NOT NULL,
            photo TEXT,
            text TEXT,
            type TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
		CREATE TABLE IF NOT EXISTS requests (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
		)
	''')

    connection.commit()


def add_user(connection, username, email, lName, password , photo_name):
    cursor = connection.cursor()
    hashed_password = check.hash_password(password)
    query = '''INSERT INTO users (username ,email ,fName ,lName , password , photo_name,wallet) VALUES (? ,? ,? ,? ,? ,?,0)'''
    cursor.execute(query, (username ,email ,username ,lName , hashed_password , photo_name))
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

def delete_user(connection, id):
    cursor = connection.cursor()
    query = ''' DELETE FROM users WHERE id = ? AND id != 1'''
    cursor.execute(query, (id,)) 
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
def get_user_id(connection, id):
    cursor = connection.cursor()
    query = '''SELECT * FROM users WHERE id = ?'''
    cursor.execute(query, (id,))
    return cursor.fetchone()

def update_wallet(connection,id,money):
    cursor = connection.cursor()  
    query = '''UPDATE users SET wallet = ? WHERE id = ? AND id != 1'''
    cursor.execute(query, (money,id))  
    connection.commit() 

# def inittable_product(conn):
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS products (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             amout INTEGER NOT NULL,
#             price INTEGER NOT NULL,
#             photo TEXT,
#             text TEXT,
#             type TEXT
#         )
#     ''')
#     conn.commit()

def add_product(conn,data):
    cur=conn.cursor()
    quary="INSERT INTO products (name,price,amout,photo,text,type) VALUES (?,?,?,?,?,?)"
    cur.execute(quary,(data['name'],data['price'],data['amout'],data['photo'],data['text'],data['type']))
    conn.commit()

def get_product(conn):
    cur=conn.cursor()
    quary="SELECT * FROM products"
    cur.execute(quary)
    return cur.fetchall()

def get_product_id(conn,id):
    cur=conn.cursor()
    quary="SELECT * FROM products WHERE id=?"
    cur.execute(quary,(id,))
    return cur.fetchone()

def update_product(conn,data,id):
    cur=conn.cursor()
    quary="UPDATE products SET name=?,price=?,amout=?,text=?,type=? WHERE id=?"
    cur.execute(quary,(data['name'],data['price'],data['amout'],data['text'],data['type'],id))
    conn.commit()
def update_amount(conn,id,amount):
    cur=conn.cursor()
    quary="UPDATE products SET amout=? WHERE id=?"
    cur.execute(quary,(amount,id))
    conn.commit()

def update_photo_product(conn,id,filename):
    cur=conn.cursor()
    quary="UPDATE products SET photo=? WHERE id=?"
    cur.execute(quary,(filename,id))
    conn.commit()
    
def delete_product(conn,id):
    cur=conn.cursor()
    quary="DELETE FROM products WHERE id=?"
    cur.execute(quary,(id,))
    conn.commit()

def get_product_search(conn,search0):
    cur =conn.cursor()
    quary="SELECT * FROM products WHERE name LIKE ?"
    cur.execute(quary,(f"%{search0}%",))
    return cur.fetchall()



    
def get_product_id(conn,id):
    cur=conn.cursor()
    quary="SELECT * FROM products WHERE id=?"
    cur.execute(quary,(id,))
    return cur.fetchone()

# def init_comments_table(conn):
#     cur = conn.cursor()

#     cur.execute('''
#         CREATE TABLE IF NOT EXISTS comments (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             product_id INTEGER NOT NULL,
#             user_id INTEGER NOT NULL,
#             text TEXT NOT NULL,
#             timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (product_id) REFERENCES products (id),
#             FOREIGN KEY (user_id) REFERENCES users (id)
#         )
#     ''')
#     conn.commit()

def add_comment(conn, product_id, user_id, text):
    cur = conn.cursor()
    query = '''INSERT INTO comments (product_id, user_id, text) VALUES (?, ?, ?)'''
    cur.execute(query, (product_id, user_id, text))
    conn.commit()

def get_comments_for_product(connection, product_id):
    cursor = connection.cursor()
    query = '''
        SELECT users.username, comments.text, comments.timestamp
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.product_id = ?
    '''
    cursor.execute(query, (product_id,))
    return cursor.fetchall()

# def init_requests(connection):
#     cursor = connection.cursor()

#     cursor.execute('''
# 		CREATE TABLE IF NOT EXISTS requests (
# 			id INTEGER PRIMARY KEY AUTOINCREMENT,
#             FOREIGN KEY (userId) REFERENCES users (id),
#             FOREIGN KEY (productId) REFERENCES products (id)
#             quantity INTEGER NOT NULL
# 		)
# 	''')
#     connection.commit()

def add_request(conn,request):
    cur=conn.cursor()
    quary="INSERT INTO requests (userId,productId,quantity) VALUES (?,?,?)"
    cur.execute(quary,(request['userId'],request['productId'],request['quantity']))
    conn.commit()

def get_request_id(conn,id):
    cur=conn.cursor()
    quary="SELECT * FROM requests WHERE id=?"
    cur.execute(quary,(id,))
    return cur.fetchone()

def update_request(conn,requestNewQuantity,id):
    cur=conn.cursor()
    quary="UPDATE requests SET quantity=? WHERE id=?"
    cur.execute(quary,(requestNewQuantity,id))
    conn.commit()

def delete_request(conn,id):
    cur=conn.cursor()
    quary="DELETE FROM requests WHERE id=?"
    cur.execute(quary,(id,))
    conn.commit()