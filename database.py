import mysql.connector


# Función de conexión
def conectar():
    return mysql.connector.connect(
        host='localhost',
        user='root',         # O el usuario de MySQL que uses
        password='',         # Si tenés clave, ponela aquí
        database='hotel'
    )

# Verifica credenciales del administrador
def check_admin_credentials(username, password):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM admins WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()
    return admin

# Crea un administrador si no existe
def create_admin(username, password):
    conn = conectar()
    cursor = conn.cursor()
    # Verifica si ya existe
    cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO admins (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
    cursor.close()
    conn.close()
