from flask import Flask, flash, render_template, request, redirect, url_for, session
from datetime import datetime
import database
import logging
from decimal import Decimal


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'clave_secreta_demo_2024'  # Cambiar en producción

@app.route('/')
def index():
    return redirect(url_for('admin_login'))

# LOGIN ADMIN
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            return render_template('admin_login.html', error="Usuario y contraseña son requeridos")

        admin = database.check_admin_credentials(username, password)
        if admin:
            session['admin'] = True
            session['admin_username'] = username
            logger.info(f"Admin {username} inició sesión")
            flash(f"Bienvenido, {username}!", "success")
            return redirect(url_for('admin_panel'))
        else:
            logger.warning(f"Intento de login fallido para usuario: {username}")
            return render_template('admin_login.html', error="Credenciales incorrectas")

    return render_template('admin_login.html')

# PANEL ADMIN
@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    # Obtener estadísticas básicas
    try:
        clientes = database.listar_clientes()
        reservas = database.listar_reservas()
        habitaciones = database.listar_todas_habitaciones()
        
        stats = {
            'total_clientes': len(clientes),
            'total_reservas': len(reservas),
            'total_habitaciones': len(habitaciones),
            'habitaciones_disponibles': len([h for h in habitaciones if h['estado'] == 'disponible']),
            'habitaciones_ocupadas': len([h for h in habitaciones if h['estado'] == 'ocupada'])
        }
        
        return render_template('admin_panel.html', stats=stats)
    except Exception as e:
        logger.error(f"Error en panel admin: {e}")
        flash("Error al cargar estadísticas", "error")
        return render_template('admin_panel.html', stats={})

# LOGOUT
@app.route('/logout')
def logout():
    username = session.get('admin_username', 'Usuario')
    session.clear()
    logger.info(f"Admin {username} cerró sesión")
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for('admin_login'))

# NUEVO CLIENTE
@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        dni = request.form.get('dni', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        direccion = request.form.get('direccion', '').strip()

        # Validaciones básicas
        if not nombre or not apellido or not dni:
            return render_template('nuevo_cliente.html', error="Nombre, apellido y DNI son obligatorios")

        # Validar formato de DNI (solo números)
        if not dni.isdigit() or len(dni) < 7:
            return render_template('nuevo_cliente.html', error="DNI debe contener solo números (mínimo 7 dígitos)")

        # Validar email si se proporciona
        if email and '@' not in email:
            return render_template('nuevo_cliente.html', error="Formato de email inválido")

        try:
            id_cliente = database.agregar_cliente(nombre, apellido, dni, telefono, email, direccion)
            if id_cliente:
                flash(f"Cliente {nombre} {apellido} registrado correctamente", "success")
                return redirect(url_for('reservar_habitacion', id_cliente=id_cliente))
            else:
                return render_template('nuevo_cliente.html', error="Error al guardar cliente. Verifique que el DNI no esté duplicado")
        except Exception as e:
            logger.error(f"Error al agregar cliente: {e}")
            return render_template('nuevo_cliente.html', error="Error interno del servidor")

    return render_template('nuevo_cliente.html')

# RESERVAR HABITACION
@app.route('/reservar/<int:id_cliente>', methods=['GET', 'POST'])
def reservar_habitacion(id_cliente):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    # Verificar que el cliente existe
    cliente = database.obtener_cliente(id_cliente)
    if not cliente:
        flash("Cliente no encontrado", "error")
        return redirect(url_for('lista_clientes'))

    habitaciones = []
    error = None
    dias = None
    monto = None

    if request.method == 'POST':
        fecha_entrada = request.form.get('fecha_entrada', '').strip()
        fecha_salida = request.form.get('fecha_salida', '').strip()

        if not fecha_entrada or not fecha_salida:
            error = "Ambas fechas son obligatorias"
            return render_template('reservar_habitacion.html', habitaciones=[], error=error, cliente=cliente)

        try:
            f1 = datetime.strptime(fecha_entrada, "%Y-%m-%dT%H:%M")
            f2 = datetime.strptime(fecha_salida, "%Y-%m-%dT%H:%M")
            dias = (f2 - f1).days if (f2 - f1).days > 0 else 1
            
            if f2 <= f1:
                error = "La fecha y hora de salida debe ser posterior a la de entrada"
                return render_template('reservar_habitacion.html', habitaciones=[], error=error, cliente=cliente)
                
            if f1 < datetime.now():
                error = "No se pueden hacer reservas para fecha y hora pasadas"
                return render_template('reservar_habitacion.html', habitaciones=[], error=error, cliente=cliente)
                
        except ValueError as e:
            error = "Formato de fecha inválido. Use el control de fecha y hora"
            return render_template('reservar_habitacion.html', habitaciones=[], error=error, cliente=cliente)

        # Si ya seleccionó habitación, confirmar reserva
        if 'habitacion' in request.form:
            id_habitacion = request.form['habitacion']
            habitacion = database.obtener_habitacion(id_habitacion)
            
            if not habitacion:
                error = "Habitación no encontrada"
                habitaciones = database.listar_habitaciones_disponibles(fecha_entrada, fecha_salida)
            else:
                precio = float(habitacion['precio_por_noche'])
                monto_total = dias * precio
                
                # Obtener porcentaje de anticipo
                porcentaje_anticipo = float(request.form.get('porcentaje_anticipo', 30))
                monto_anticipo = (monto_total * porcentaje_anticipo) / 100

                reserva_id = database.reservar_habitacion(id_cliente, id_habitacion, fecha_entrada, fecha_salida, monto_total)
                if reserva_id:
                    anticipo_info = database.crear_anticipo(reserva_id, porcentaje_anticipo)
                    if anticipo_info:
                        flash(f"Reserva confirmada para {cliente['nombre']} {cliente['apellido']}. Días: {dias}, Total: ${monto_total:,.2f}, Anticipo: ${monto_anticipo:,.2f} ({porcentaje_anticipo}%)", "success")
                    else:
                        flash(f"Reserva confirmada para {cliente['nombre']} {cliente['apellido']}. Días: {dias}, Total: ${monto_total:,.2f}", "success")
                    return redirect(url_for('lista_reservas'))
                else:
                    error = "Habitación no disponible en esas fechas"
                    habitaciones = database.listar_habitaciones_disponibles(fecha_entrada, fecha_salida)
        else:
            # Solo buscar habitaciones disponibles
            habitaciones = database.listar_habitaciones_disponibles(fecha_entrada, fecha_salida)
            if not habitaciones:
                error = "No hay habitaciones disponibles para las fechas seleccionadas"

    return render_template('reservar_habitacion.html', habitaciones=habitaciones, error=error, dias=dias, monto=monto, cliente=cliente)



# LISTAR CLIENTES
@app.route('/clientes')
def lista_clientes():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    try:
        clientes = database.listar_clientes()
        return render_template('lista_clientes.html', clientes=clientes)
    except Exception as e:
        logger.error(f"Error al listar clientes: {e}")
        flash("Error al cargar lista de clientes", "error")
        return render_template('lista_clientes.html', clientes=[])

# LISTAR RESERVAS
@app.route('/reservas')
def lista_reservas():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    try:
        reservas = database.listar_reservas_con_anticipos()
        return render_template('lista_reservas.html', reservas=reservas)
    except Exception as e:
        logger.error(f"Error al listar reservas: {e}")
        flash("Error al cargar lista de reservas", "error")
        return render_template('lista_reservas.html', reservas=[])

@app.route('/habitaciones')
def lista_habitaciones():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    try:
        habitaciones = database.listar_todas_habitaciones()
        return render_template('lista_habitaciones.html', habitaciones=habitaciones)
    except Exception as e:
        logger.error(f"Error al listar habitaciones: {e}")
        flash("Error al cargar lista de habitaciones", "error")
        return render_template('lista_habitaciones.html', habitaciones=[])

@app.route('/habitaciones/estado', methods=['GET', 'POST'])
def cambiar_estado_habitaciones():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    try:
        habitaciones = database.listar_todas_habitaciones()

        if request.method == 'POST':
            id_habitacion = request.form.get('habitacion_id', '').strip()
            nuevo_estado = request.form.get('nuevo_estado', '').strip()
            
            if not id_habitacion or not nuevo_estado:
                flash("Seleccione una habitación y un estado", "error")
            else:
                exito = database.cambiar_estado_habitacion(id_habitacion, nuevo_estado)
                if exito:
                    flash(f"Estado de habitación {id_habitacion} actualizado a {nuevo_estado}", "success")
                else:
                    flash("Error al actualizar el estado de la habitación", "error")
        return render_template('cambiar_estado_habitaciones.html', habitaciones=habitaciones)
        #return redirect(url_for('cambiar_estado_habitaciones'))

    except Exception as e:
        logger.error(f"Error en cambiar estado habitaciones: {e}")
        flash("Error al cargar habitaciones", "error")
        return render_template('cambiar_estado_habitaciones.html', habitaciones=[])

@app.route('/reservas/extender/<int:id_reserva>', methods=['GET', 'POST'])
def extender_reserva_ruta(id_reserva):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    try:
        reserva = database.obtener_reserva(id_reserva)
        if not reserva:
            flash("Reserva no encontrada", "error")
            return redirect(url_for('lista_reservas'))

        if request.method == 'POST':
            nueva_fecha_salida = request.form.get('fecha_salida', '').strip()
            
            if not nueva_fecha_salida:
                return render_template('extender_reserva.html', reserva=reserva, error="Fecha de salida es obligatoria")
            
            try:
                # Validar que la nueva fecha sea posterior a la actual
                fecha_actual = datetime.strptime(reserva['fecha_salida'], "%Y-%m-%d %H:%M:%S")
                nueva_fecha = datetime.strptime(nueva_fecha_salida, "%Y-%m-%dT%H:%M")
                
                if nueva_fecha <= fecha_actual:
                    return render_template('extender_reserva.html', reserva=reserva, error="La nueva fecha debe ser posterior a la fecha actual de salida")
                
                exito = database.extender_reserva(id_reserva, nueva_fecha_salida)
                if exito:
                    flash(f"Reserva extendida hasta {nueva_fecha_salida}", "success")
                    return redirect(url_for('lista_reservas'))
                else:
                    error = "No se puede extender la reserva, hay conflicto con otra reserva futura"
                    return render_template('extender_reserva.html', reserva=reserva, error=error)
            except ValueError:
                return render_template('extender_reserva.html', reserva=reserva, error="Formato de fecha inválido")

    except Exception as e:
        logger.error(f"Error en extender reserva: {e}")
        flash("Error al procesar la extensión de reserva", "error")
        return redirect(url_for('lista_reservas'))

@app.route('/modificar_precio', methods=['POST'])
def modificar_precio():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    try:
        id_habitacion = request.form.get('id_habitacion', '').strip()
        precio_nuevo = request.form.get('precio_por_noche', '').strip()
        nuevo_estado = request.form.get('nuevo_estado', '').strip()

        if not id_habitacion or not precio_nuevo or not nuevo_estado:
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('lista_habitaciones'))

        precio_nuevo = float(precio_nuevo)
        if precio_nuevo <= 0:
            flash('El precio debe ser mayor a 0', 'error')
            return redirect(url_for('lista_habitaciones'))

        exito = database.cambiar_precio_y_estado_habitacion(id_habitacion, precio_nuevo, nuevo_estado)
        if exito:
            flash('Precio y estado actualizados correctamente', 'success')
        else:
            flash('Error al actualizar la habitación', 'error')
            
    except ValueError:
        flash('El precio ingresado no es válido', 'error')
    except Exception as e:
        logger.error(f"Error al modificar precio: {e}")
        flash('Error interno del servidor', 'error')

    return redirect(url_for('lista_habitaciones'))

# MARCAR RESERVA COMO OCUPADA
@app.route('/reservas/marcar_ocupada/<int:id_reserva>', methods=['POST'])
def marcar_reserva_ocupada(id_reserva):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    try:
        # Obtener información de la reserva
        reserva = database.obtener_reserva(id_reserva)
        if not reserva:
            flash("Reserva no encontrada", "error")
            return redirect(url_for('lista_reservas'))
        
        # Cambiar estado de la reserva a 'ocupada'
        exito = database.cambiar_estado_reserva(id_reserva, 'ocupada')
        if exito:
            # Cambiar estado de la habitación a 'ocupada'
            database.cambiar_estado_habitacion(reserva['id_habitacion'], 'ocupada')
            flash(f"Reserva #{id_reserva} marcada como ocupada", "success")
        else:
            flash("Error al marcar la reserva como ocupada", "error")
            
    except Exception as e:
        logger.error(f"Error al marcar reserva como ocupada: {e}")
        flash("Error interno del servidor", "error")
    
    return redirect(url_for('lista_reservas'))

# CANCELAR RESERVA
@app.route('/reservas/cancelar/<int:id_reserva>', methods=['POST'])
def cancelar_reserva(id_reserva):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    try:
        # Obtener información de la reserva
        reserva = database.obtener_reserva(id_reserva)
        if not reserva:
            flash("Reserva no encontrada", "error")
            return redirect(url_for('lista_reservas'))
        
        # Cambiar estado de la reserva a 'cancelada'
        exito = database.cambiar_estado_reserva(id_reserva, 'cancelada')
        if exito:
            # Liberar la habitación (cambiar a 'disponible')
            database.cambiar_estado_habitacion(reserva['id_habitacion'], 'disponible')
            flash(f"Reserva #{id_reserva} cancelada y habitación liberada", "success")
        else:
            flash("Error al cancelar la reserva", "error")
            
    except Exception as e:
        logger.error(f"Error al cancelar reserva: {e}")
        flash("Error interno del servidor", "error")
    
    return redirect(url_for('lista_reservas'))


if __name__ == '__main__':
    app.run(debug=True)
