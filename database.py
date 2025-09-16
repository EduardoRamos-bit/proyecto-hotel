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
    cursor.execute("""
        SELECT c.*, r.fecha_salida
        FROM clientes c
        LEFT JOIN reservas r ON c.id_cliente = r.id_cliente
        ORDER BY c.id_cliente
    """)
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return clientes

def listar_habitaciones_disponibles(fecha_entrada, fecha_salida):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * 
        FROM habitaciones h
        WHERE h.id NOT IN (
            SELECT r.id_habitacion
            FROM reservas r
            WHERE NOT (r.fecha_salida <= %s OR r.fecha_entrada >= %s)
        )
        AND h.estado = 'disponible'
    """
    # Aquí ponemos primero fecha_entrada, luego fecha_salida
    cursor.execute(query, (fecha_entrada, fecha_salida))
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

def reservar_habitacion(id_cliente, id_habitacion, fecha_entrada, fecha_salida, monto):
    conn = conectar()
    cursor = conn.cursor()
    try:
        # Verificar si hay solapamiento
        cursor.execute("""
            SELECT 1 
            FROM reservas 
            WHERE id_habitacion = %s
              AND NOT (fecha_salida <= %s OR fecha_entrada >= %s)
        """, (id_habitacion, fecha_entrada, fecha_salida))
        conflicto = cursor.fetchone()
        if conflicto:
            return False

        # Insertar reserva
        cursor.execute("""
            INSERT INTO reservas (id_cliente, id_habitacion, fecha_entrada, fecha_salida, monto)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_cliente, id_habitacion, fecha_entrada, fecha_salida, monto))

        # Cambiar estado de la habitación a ocupada
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
    
    # Traemos todas las habitaciones
    cursor.execute("SELECT * FROM habitaciones ORDER BY numero_habitacion")
    habitaciones = cursor.fetchall()
    
    # Por cada habitación, agregamos sus reservas futuras/actuales
    for hab in habitaciones:
        cursor.execute("""
            SELECT fecha_entrada, fecha_salida
            FROM reservas
            WHERE id_habitacion = %s
              AND fecha_salida >= CURDATE()
            ORDER BY fecha_entrada
        """, (hab['id'],))
        hab['reservas'] = cursor.fetchall()
    
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

def cambiar_precio_y_estado_habitacion(id_habitacion, precio, estado):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE habitaciones
        SET precio_por_noche = %s,
            estado = %s
        WHERE id = %s
    """, (precio, estado, id_habitacion))
    conn.commit()
    cursor.close()
    conn.close()

    
def obtener_habitacion(id_habitacion):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM habitaciones WHERE id = %s", (id_habitacion,))
    habitacion = cursor.fetchone()
    cursor.close()
    conn.close()
    return habitacion
    