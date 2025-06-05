import sqlite3
import hashlib

DATABASE = 'hotel.db'

def get_db():
    return sqlite3.connect(DATABASE)

def create_tables():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        conn.commit()

def create_admin(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            print(f"Administrador '{username}' creado exitosamente.")
    except sqlite3.IntegrityError:
        print(f"El administrador '{username}' ya existe.")

def check_admin_credentials(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM admins WHERE username = ? AND password = ?', (username, hashed_password))
        return cursor.fetchone()
