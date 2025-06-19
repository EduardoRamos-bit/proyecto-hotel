import mysql.connector
from mysql.connector import Error
import hashlib

# Configuración de conexión a MySQL
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'tu_usuario',
    'password': 'tu_contraseña',
    'database': 'hotel'
}

def get_db():
    return mysql.connector.connect(**DATABASE_CONFIG)

def create_tables():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error al crear tablas: {e}")

def create_admin(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO admins (username, password) VALUES (%s, %s)', (username, hashed_password))
        conn.commit()
        print(f"Administrador '{username}' creado exitosamente.")
    except mysql.connector.IntegrityError:
        print(f"El administrador '{username}' ya existe.")
    except Error as e:
        print(f"Error al crear admin: {e}")
    finally:
        cursor.close()
        conn.close()

def check_admin_credentials(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE username = %s AND password = %s', (username, hashed_password))
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"Error al verificar credenciales: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def create_tables():
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Tabla de administradores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')

        # Tabla de clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                dni VARCHAR(20),
                pasaporte VARCHAR(20)
            )
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        print("Tablas creadas correctamente.")
    except Error as e:
        print(f"Error al crear tablas: {e}")
