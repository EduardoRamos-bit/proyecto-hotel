import mysql.connector
from datetime import datetime
import logging
from decimal import Decimal

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def conectar():
    """Establece conexión con la base de datos"""
    try:
        conn = mysql.connector.connect(
        host='localhost',
        user='root',         
        password='',         
            database='hotel',
            charset='utf8mb4',
            collation='utf8mb4_general_ci'
    )
        return conn
    except mysql.connector.Error as e:
        logger.error(f"Error de conexión a la base de datos: {e}")
        raise

def check_admin_credentials(username, password):
    """Verifica las credenciales del administrador"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM admins WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        admin = cursor.fetchone()
        return admin
    except mysql.connector.Error as e:
        logger.error(f"Error al verificar credenciales: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_admin(username, password):
    """Crea un nuevo administrador si no existe"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO admins (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            return True
        return False
    except mysql.connector.Error as e:
        logger.error(f"Error al crear administrador: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def agregar_cliente(nombre, apellido, dni, telefono, email, direccion):
    """Agrega un nuevo cliente a la base de datos"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # Validar que el DNI no exista
        cursor.execute("SELECT id_cliente FROM clientes WHERE dni_pasaporte_cpf = %s", (dni,))
        if cursor.fetchone():
            logger.warning(f"Cliente con DNI {dni} ya existe")
            return None
            
        sql = """
            INSERT INTO clientes (nombre, apellido, dni_pasaporte_cpf, telefono, email, direccion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (nombre, apellido, dni, telefono, email, direccion))
        conn.commit()
        last_id = cursor.lastrowid
        logger.info(f"Cliente agregado con ID: {last_id}")
        return last_id
    except mysql.connector.Error as e:
        logger.error(f"Error al agregar cliente: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def obtener_cliente(id_cliente):
    """Obtiene un cliente por su ID"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_cliente,))
        cliente = cursor.fetchone()
        return cliente
    except mysql.connector.Error as e:
        logger.error(f"Error al obtener cliente: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def listar_clientes():
    """Lista todos los clientes con información completa de reservas"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                c.id_cliente,
                c.nombre,
                c.apellido,
                c.dni_pasaporte_cpf,
                c.telefono,
                c.email,
                c.direccion,
                c.fecha_registro,
                r.fecha_entrada,
                r.fecha_salida,
                r.monto,
                r.estado as estado_reserva,
                h.numero_habitacion,
                h.tipo as tipo_habitacion,
                p.metodo_pago,
                p.monto as monto_pagado
        FROM clientes c
            LEFT JOIN reservas r ON c.id_cliente = r.id_cliente AND r.estado = 'confirmada'
            LEFT JOIN habitaciones h ON r.id_habitacion = h.id
            LEFT JOIN pagos p ON r.id = p.id_reserva
            ORDER BY c.id_cliente, r.fecha_entrada DESC
        """)
        clientes = cursor.fetchall()
        return clientes
    except mysql.connector.Error as e:
        logger.error(f"Error al listar clientes: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def listar_clientes_filtrado(q):
    """Lista clientes filtrando por nombre, apellido o DNI (case-insensitive)."""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        like = f"%{q}%"
        cursor.execute("""
            SELECT 
                c.id_cliente,
                c.nombre,
                c.apellido,
                c.dni_pasaporte_cpf,
                c.telefono,
                c.email,
                c.direccion,
                c.fecha_registro,
                r.fecha_entrada,
                r.fecha_salida,
                r.monto,
                r.estado as estado_reserva,
                h.numero_habitacion,
                h.tipo as tipo_habitacion
            FROM clientes c
            LEFT JOIN reservas r ON c.id_cliente = r.id_cliente AND r.estado IN ('confirmada','ocupada')
            LEFT JOIN habitaciones h ON r.id_habitacion = h.id
            WHERE c.nombre LIKE %s OR c.apellido LIKE %s OR c.dni_pasaporte_cpf LIKE %s
            ORDER BY c.id_cliente, r.fecha_entrada DESC
        """, (like, like, like))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        logger.error(f"Error al filtrar clientes: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def listar_habitaciones_disponibles(fecha_entrada, fecha_salida):
    """Lista habitaciones disponibles para un rango de fecha y hora"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        
        # Validar fechas (datetime)
        fecha_entrada_dt = datetime.strptime(fecha_entrada, "%Y-%m-%dT%H:%M")
        fecha_salida_dt = datetime.strptime(fecha_salida, "%Y-%m-%dT%H:%M")
        
        if fecha_entrada_dt >= fecha_salida_dt:
            logger.warning("Fecha de entrada debe ser anterior a fecha de salida")
            return []
        
        if fecha_entrada_dt < datetime.now():
            logger.warning("No se pueden hacer reservas para fecha y hora pasadas")
            return []
        
        query = """
        SELECT * 
        FROM habitaciones h
        WHERE h.id NOT IN (
            SELECT r.id_habitacion
            FROM reservas r
            WHERE r.estado = 'confirmada'
              AND NOT (r.fecha_salida <= %s OR r.fecha_entrada >= %s)
        )
        AND h.estado = 'disponible'
        ORDER BY h.numero_habitacion
        """
        cursor.execute(query, (fecha_entrada_dt, fecha_salida_dt))
        habitaciones = cursor.fetchall()
        logger.info(f"Encontradas {len(habitaciones)} habitaciones disponibles")
        return habitaciones
    except mysql.connector.Error as e:
        logger.error(f"Error al listar habitaciones disponibles: {e}")
        return []
    except ValueError as e:
        logger.error(f"Error en formato de fechas: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



def cambiar_estado_habitacion(id_habitacion, nuevo_estado):
    """Cambia el estado de una habitación"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE habitaciones SET estado = %s WHERE id = %s", (nuevo_estado, id_habitacion))
        conn.commit()
        logger.info(f"Estado de habitación {id_habitacion} cambiado a {nuevo_estado}")
        return True
    except mysql.connector.Error as e:
        logger.error(f"Error al cambiar estado de habitación: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def reservar_habitacion(id_cliente, id_habitacion, fecha_entrada, fecha_salida, monto):
    """Reserva una habitación para un cliente y devuelve el id de la reserva creada"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        fecha_entrada_dt = datetime.strptime(fecha_entrada, "%Y-%m-%dT%H:%M")
        fecha_salida_dt = datetime.strptime(fecha_salida, "%Y-%m-%dT%H:%M")
        
        # Verificar solapamiento con reservas confirmadas (por datetime)
        cursor.execute("""
            SELECT 1 
            FROM reservas 
            WHERE id_habitacion = %s
              AND estado = 'confirmada'
              AND NOT (fecha_salida <= %s OR fecha_entrada >= %s)
        """, (id_habitacion, fecha_entrada_dt, fecha_salida_dt))
        conflicto = cursor.fetchone()
        if conflicto:
            logger.warning(f"Conflicto de fechas/horas para habitación {id_habitacion}")
            return False

        # Verificar que la habitación esté disponible
        cursor.execute("SELECT estado FROM habitaciones WHERE id = %s", (id_habitacion,))
        habitacion = cursor.fetchone()
        if not habitacion or habitacion[0] != 'disponible':
            logger.warning(f"Habitación {id_habitacion} no está disponible")
            return False

        # Insertar reserva con datetime
        cursor.execute("""
            INSERT INTO reservas (id_cliente, id_habitacion, fecha_entrada, fecha_salida, monto, estado)
            VALUES (%s, %s, %s, %s, %s, 'confirmada')
        """, (id_cliente, id_habitacion, fecha_entrada_dt, fecha_salida_dt, monto))
        reserva_id = cursor.lastrowid

        # No cambiar estado de la habitación a 'ocupada' hasta el check-in efectivo
        # Se mantiene 'disponible' hasta que llegue la hora de entrada

        conn.commit()
        logger.info(f"Reserva creada para habitación {id_habitacion}, cliente {id_cliente}, reserva {reserva_id}")
        return reserva_id
    except mysql.connector.Error as e:
        logger.error(f"Error al reservar habitación: {e}")
        if conn:
            conn.rollback()
        return None
    except ValueError as e:
        logger.error(f"Formato de fecha/hora inválido: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



def listar_reservas():
    """Lista todas las reservas con información de clientes y habitaciones"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, c.nombre, c.apellido, h.numero_habitacion
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            JOIN habitaciones h ON r.id_habitacion = h.id
            ORDER BY r.fecha_entrada DESC
        """)
        reservas = cursor.fetchall()
        return reservas
    except mysql.connector.Error as e:
        logger.error(f"Error al listar reservas: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def listar_todas_habitaciones():
    """Lista todas las habitaciones con sus reservas futuras (con hora)"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM habitaciones ORDER BY numero_habitacion")
        habitaciones = cursor.fetchall()
        
        for hab in habitaciones:
            cursor.execute("""
                SELECT fecha_entrada, fecha_salida, estado
                FROM reservas
                WHERE id_habitacion = %s
                  AND fecha_salida >= NOW()
                  AND estado = 'confirmada'
                ORDER BY fecha_entrada
            """, (hab['id'],))
            hab['reservas'] = cursor.fetchall()
        
        return habitaciones
    except mysql.connector.Error as e:
        logger.error(f"Error al listar habitaciones: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def extender_reserva(id_reserva, nueva_fecha_salida):
    """Extiende una reserva existente (con hora)"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_habitacion, fecha_salida, monto FROM reservas WHERE id = %s AND estado = 'confirmada'", (id_reserva,))
        reserva = cursor.fetchone()
        if not reserva:
            logger.warning(f"Reserva {id_reserva} no encontrada o no confirmada")
            return False

        id_habitacion, fecha_salida_actual, monto_actual = reserva

        # Verificar que no haya reservas futuras que choquen
        cursor.execute("""
            SELECT 1 FROM reservas
            WHERE id_habitacion = %s 
              AND estado = 'confirmada'
              AND fecha_entrada > %s 
              AND fecha_entrada <= %s
        """, (id_habitacion, fecha_salida_actual, datetime.strptime(nueva_fecha_salida, "%Y-%m-%dT%H:%M")))
        conflicto = cursor.fetchone()
        if conflicto:
            logger.warning(f"No se puede extender reserva {id_reserva}, hay conflicto")
            return False

        # Calcular nuevo monto por días completos adicionales (mantener lógica actual)
        dias_adicionales = (datetime.strptime(nueva_fecha_salida, "%Y-%m-%dT%H:%M") - fecha_salida_actual).days
        if dias_adicionales <= 0:
            logger.warning("La nueva fecha debe ser posterior a la actual")
            return False
            
        cursor.execute("SELECT precio_por_noche FROM habitaciones WHERE id = %s", (id_habitacion,))
        precio_noche = cursor.fetchone()[0]
        nuevo_monto = float(monto_actual) + (dias_adicionales * float(precio_noche))

        cursor.execute("UPDATE reservas SET fecha_salida = %s, monto = %s WHERE id = %s", 
                       (datetime.strptime(nueva_fecha_salida, "%Y-%m-%dT%H:%M"), nuevo_monto, id_reserva))
        conn.commit()
        logger.info(f"Reserva {id_reserva} extendida hasta {nueva_fecha_salida}")
        return True
    except mysql.connector.Error as e:
        logger.error(f"Error al extender reserva: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def cambiar_precio_y_estado_habitacion(id_habitacion, precio, estado):
    """Cambia el precio y estado de una habitación"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE habitaciones
            SET precio_por_noche = %s,
                estado = %s
            WHERE id = %s
        """, (precio, estado, id_habitacion))
        conn.commit()
        logger.info(f"Precio y estado de habitación {id_habitacion} actualizados")
        return True
    except mysql.connector.Error as e:
        logger.error(f"Error al actualizar habitación: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
def obtener_habitacion(id_habitacion):
    """Obtiene una habitación por su ID"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM habitaciones WHERE id = %s", (id_habitacion,))
        habitacion = cursor.fetchone()
        return habitacion
    except mysql.connector.Error as e:
        logger.error(f"Error al obtener habitación: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def obtener_reserva(id_reserva):
    """Obtiene una reserva por su ID"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, c.nombre, c.apellido, h.numero_habitacion
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            JOIN habitaciones h ON r.id_habitacion = h.id
            WHERE r.id = %s
        """, (id_reserva,))
        reserva = cursor.fetchone()
        return reserva
    except mysql.connector.Error as e:
        logger.error(f"Error al obtener reserva: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

<<<<<<< HEAD

def marcar_reserva_y_habitacion_ocupada(id_reserva):
    """Marca la reserva como 'ocupada' y actualiza la habitación asociada a 'ocupada'.

    Retorna True si ambas actualizaciones se realizaron correctamente, False en caso contrario.
    """
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Obtener la habitación asociada a la reserva
        cursor.execute("SELECT id_habitacion FROM reservas WHERE id = %s", (id_reserva,))
        row = cursor.fetchone()
        if not row:
            logger.warning(f"Reserva {id_reserva} no encontrada para marcar ocupada")
            return False

        id_habitacion = row[0]

        # Actualizar estado de la reserva (si tiene columna estado) y la habitación
        cursor.execute("UPDATE reservas SET estado = 'ocupada' WHERE id = %s", (id_reserva,))
        cursor.execute("UPDATE habitaciones SET estado = 'ocupada' WHERE id = %s", (id_habitacion,))
        conn.commit()
        logger.info(f"Reserva {id_reserva} y habitación {id_habitacion} marcadas como ocupadas")
        return True
    except mysql.connector.Error as e:
        logger.error(f"Error al marcar reserva/habitación ocupada: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def cancelar_reserva(id_reserva):
    """Cancela una reserva y libera la habitación asociada (estado 'disponible')."""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT id_habitacion FROM reservas WHERE id = %s", (id_reserva,))
        row = cursor.fetchone()
        if not row:
            return False
        id_habitacion = row[0]

        cursor.execute("UPDATE reservas SET estado = 'cancelada' WHERE id = %s", (id_reserva,))
        cursor.execute("UPDATE habitaciones SET estado = 'disponible' WHERE id = %s", (id_habitacion,))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        logger.error(f"Error al cancelar reserva: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

=======
>>>>>>> 2d47f5e02a159cd5177746f01b89d2d89bcb38bb
def crear_anticipo(id_reserva, porcentaje_anticipo):
    """Crea un anticipo para una reserva"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # Obtener monto total de la reserva
        cursor.execute("SELECT monto FROM reservas WHERE id = %s", (id_reserva,))
        reserva = cursor.fetchone()
        if not reserva:
            return None
            
        monto_total = reserva[0]
        # Convertir porcentaje_anticipo a Decimal para operaciones monetarias
        porcentaje_decimal = Decimal(str(porcentaje_anticipo))
        monto_anticipo = (monto_total * porcentaje_decimal) / 100
        monto_restante = monto_total - monto_anticipo
        
        # Insertar anticipo
        cursor.execute("""
            INSERT INTO anticipos (id_reserva, monto_total, porcentaje_anticipo, monto_anticipo, monto_restante)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_reserva, monto_total, porcentaje_anticipo, monto_anticipo, monto_restante))
        
        # Actualizar reserva con datos de anticipo
        cursor.execute("""
            UPDATE reservas 
            SET monto_anticipo = %s, porcentaje_anticipo = %s
            WHERE id = %s
        """, (monto_anticipo, porcentaje_anticipo, id_reserva))
        
        conn.commit()
        logger.info(f"Anticipo creado para reserva {id_reserva}: ${monto_anticipo}")
        return {
            'monto_total': monto_total,
            'monto_anticipo': monto_anticipo,
            'monto_restante': monto_restante
        }
    except mysql.connector.Error as e:
        logger.error(f"Error al crear anticipo: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def listar_reservas_con_anticipos():
    """Lista todas las reservas con información de anticipos"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                r.id,
                r.fecha_entrada,
                r.fecha_salida,
                r.monto as monto_total,
                r.monto_anticipo,
                r.porcentaje_anticipo,
                (r.monto - COALESCE(r.monto_anticipo, 0)) as monto_restante,
                r.estado as estado_reserva,
                c.nombre,
                c.apellido,
                c.dni_pasaporte_cpf,
                h.numero_habitacion,
                h.tipo as tipo_habitacion
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            JOIN habitaciones h ON r.id_habitacion = h.id
            ORDER BY r.fecha_entrada DESC
        """)
        reservas = cursor.fetchall()
        return reservas
    except mysql.connector.Error as e:
        logger.error(f"Error al listar reservas con anticipos: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
<<<<<<< HEAD
def liberar_habitaciones_vencidas():
    """Libera habitaciones marcadas 'ocupada' cuyas reservas asociadas ya pasaron la fecha_salida.

    También marca esas reservas como 'finalizada'.
    """
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Seleccionar reservas ocupadas vencidas
        cursor.execute("""
            SELECT r.id, r.id_habitacion
            FROM reservas r
            WHERE r.estado = 'ocupada' AND r.fecha_salida <= NOW()
        """)
        rows = cursor.fetchall()
        if not rows:
            return 0

        reserva_ids = [row[0] for row in rows]
        habitacion_ids = [row[1] for row in rows]

        # Marcar reservas como finalizadas
        cursor.execute(
            "UPDATE reservas SET estado = 'finalizada' WHERE id IN (" + ",".join(["%s"]*len(reserva_ids)) + ")",
            reserva_ids
        )

        # Liberar habitaciones
        cursor.execute(
            "UPDATE habitaciones SET estado = 'disponible' WHERE id IN (" + ",".join(["%s"]*len(habitacion_ids)) + ")",
            habitacion_ids
        )

        conn.commit()
        logger.info(f"Liberadas {len(habitacion_ids)} habitaciones por reservas vencidas")
        return len(habitacion_ids)
    except mysql.connector.Error as e:
        logger.error(f"Error al liberar habitaciones vencidas: {e}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
=======
>>>>>>> 2d47f5e02a159cd5177746f01b89d2d89bcb38bb
