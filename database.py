import mysql.connector

def conectar():
    return mysql.connector.connect(
        host='localhost',
        user='root',         
        password='',         
        database='hotel'
    )

def check_admin_credentials(username, password):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM admins WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()
    return admin

def create_admin(username, password):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO admins (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
    cursor.close()
    conn.close()

def agregar_cliente(nombre, apellido, dni, telefono, email, direccion):
    conn = conectar()
    cursor = conn.cursor()
    sql = """
        INSERT INTO clientes (nombre, apellido, dni_pasaporte_cpf, telefono, email, direccion)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (nombre, apellido, dni, telefono, email, direccion))
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id

def obtener_cliente(id_cliente):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_cliente,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()
    return cliente

def listar_clientes():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return clientes

def listar_habitaciones_disponibles():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM habitaciones WHERE estado = 'disponible'")
    habitaciones = cursor.fetchall()
    cursor.close()
    conn.close()
    return habitaciones

def cambiar_estado_habitacion(id_habitacion, nuevo_estado):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE habitaciones SET estado = %s WHERE id = %s", (nuevo_estado, id_habitacion))
    conn.commit()
    cursor.close()
    conn.close()

def reservar_habitacion(id_cliente, id_habitacion, fecha_entrada, fecha_salida):
    conn = conectar()
    cursor = conn.cursor()
    try:
        # Verificar si la habitación está disponible
        cursor.execute("SELECT estado FROM habitaciones WHERE id = %s", (id_habitacion,))
        estado = cursor.fetchone()
        if not estado or estado[0] != 'disponible':
            return False

        # Insertar la reserva
        sql = """
            INSERT INTO reservas (id_cliente, id_habitacion, fecha_entrada, fecha_salida)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (id_cliente, id_habitacion, fecha_entrada, fecha_salida))

        # Cambiar estado de la habitación (misma conexión)
        cursor.execute("UPDATE habitaciones SET estado = 'ocupada' WHERE id = %s", (id_habitacion,))

        conn.commit()
        return True
    except Exception as e:
        print("Error en reservar_habitacion:", e)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def listar_reservas():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, c.nombre, c.apellido, h.numero_habitacion
        FROM reservas r
        JOIN clientes c ON r.id_cliente = c.id_cliente
        JOIN habitaciones h ON r.id_habitacion = h.id
    """)
    reservas = cursor.fetchall()
    cursor.close()
    conn.close()
    return reservas

def listar_todas_habitaciones():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT h.*, 
               r_ultima.fecha_salida AS fecha_salida_ultima,
               r_proxima.fecha_entrada AS fecha_entrada_proxima
        FROM habitaciones h
        LEFT JOIN (
            SELECT id_habitacion, MAX(fecha_salida) AS fecha_salida
            FROM reservas
            GROUP BY id_habitacion
        ) r_ultima ON h.id = r_ultima.id_habitacion
        LEFT JOIN (
            SELECT id_habitacion, MIN(fecha_entrada) AS fecha_entrada
            FROM reservas
            WHERE fecha_entrada > NOW()
            GROUP BY id_habitacion
        ) r_proxima ON h.id = r_proxima.id_habitacion
        ORDER BY h.numero_habitacion
    """)
    habitaciones = cursor.fetchall()
    cursor.close()
    conn.close()
    return habitaciones
def extender_reserva(id_reserva, nueva_fecha_salida):
    conn = conectar()
    cursor = conn.cursor()
    try:
        # Obtener datos de la reserva actual
        cursor.execute("SELECT id_habitacion, fecha_salida FROM reservas WHERE id = %s", (id_reserva,))
        reserva = cursor.fetchone()
        if not reserva:
            return False

        id_habitacion, fecha_salida_actual = reserva

        # Verificar que no haya reservas futuras que choquen
        cursor.execute("""
            SELECT * FROM reservas
            WHERE id_habitacion = %s AND fecha_entrada > %s AND fecha_entrada <= %s
        """, (id_habitacion, fecha_salida_actual, nueva_fecha_salida))
        conflicto = cursor.fetchone()
        if conflicto:
            return False  # No se puede extender, hay otra reserva

        # Actualizar la fecha de salida
        cursor.execute("UPDATE reservas SET fecha_salida = %s WHERE id = %s", (nueva_fecha_salida, id_reserva))
        conn.commit()
        return True
    except Exception as e:
        print("Error al extender reserva:", e)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
    