from flask import Flask, flash, render_template, request, redirect, url_for, session
import database

app = Flask(__name__)
app.secret_key = 'clave_secreta'

@app.route('/')
def index():
    return redirect(url_for('admin_login'))

# LOGIN ADMIN
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = database.check_admin_credentials(username, password)
        if admin:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template('admin_login.html', error="Credenciales incorrectas")

    return render_template('admin_login.html')

# PANEL ADMIN
@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_panel.html')

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

# NUEVO CLIENTE
@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        dni = request.form['dni']
        telefono = request.form['telefono']
        email = request.form['email']
        direccion = request.form['direccion']

        id_cliente = database.agregar_cliente(nombre, apellido, dni, telefono, email, direccion)
        if id_cliente:
            return redirect(url_for('reservar_habitacion', id_cliente=id_cliente))
        else:
            return render_template('nuevo_cliente.html', error="Error al guardar cliente")

    return render_template('nuevo_cliente.html')

# RESERVAR HABITACION
from datetime import datetime

@app.route('/reservar/<int:id_cliente>', methods=['GET', 'POST'])
def reservar_habitacion(id_cliente):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    habitaciones = []
    error = None
    dias = None
    monto = None

    if request.method == 'POST':
        fecha_entrada = request.form['fecha_entrada']
        fecha_salida = request.form['fecha_salida']

        try:
            f1 = datetime.strptime(fecha_entrada, "%Y-%m-%d")
            f2 = datetime.strptime(fecha_salida, "%Y-%m-%d")
            dias = (f2 - f1).days
            if dias <= 0:
                raise ValueError("La fecha de salida debe ser mayor a la de entrada")
        except Exception as e:
            error = str(e)
            return render_template('reservar_habitacion.html', habitaciones=[], error=error)

        # Si ya seleccionó habitación, confirmar reserva
        if 'habitacion' in request.form:
            id_habitacion = request.form['habitacion']
            habitacion = database.obtener_habitacion(id_habitacion)
            precio = habitacion['precio_por_noche']
            monto = dias * precio

            exito = database.reservar_habitacion(id_cliente, id_habitacion, fecha_entrada, fecha_salida, monto)
            if exito:
                flash(f"Reserva confirmada. Días: {dias}, Total: ${monto}")
                return redirect(url_for('lista_reservas'))
            else:
                error = "Habitación no disponible"
                # Si falla, recargar habitaciones disponibles para esas fechas
                habitaciones = database.listar_habitaciones_disponibles(fecha_entrada, fecha_salida)
        else:
            # Solo buscar habitaciones disponibles
            habitaciones = database.listar_habitaciones_disponibles(fecha_entrada, fecha_salida)

    return render_template('reservar_habitacion.html', habitaciones=habitaciones, error=error, dias=dias, monto=monto)



# LISTAR CLIENTES
@app.route('/clientes')
def lista_clientes():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    clientes = database.listar_clientes()
    return render_template('lista_clientes.html', clientes=clientes)

# LISTAR RESERVAS
@app.route('/reservas')
def lista_reservas():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    reservas = database.listar_reservas()
    return render_template('lista_reservas.html', reservas=reservas)

@app.route('/habitaciones')
def lista_habitaciones():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    habitaciones = database.listar_todas_habitaciones()  # Función que lista todo sin filtro
    return render_template('lista_habitaciones.html', habitaciones=habitaciones)

@app.route('/habitaciones/estado', methods=['GET', 'POST'])
def cambiar_estado_habitaciones():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    habitaciones = database.listar_todas_habitaciones()

    if request.method == 'POST':
        id_habitacion = request.form['habitacion_id']
        nuevo_estado = request.form['nuevo_estado']
        database.cambiar_estado_habitacion(id_habitacion, nuevo_estado)
        flash(f"Estado de habitación {id_habitacion} actualizado a {nuevo_estado}.")
        return redirect(url_for('cambiar_estado_habitaciones'))

    return render_template('cambiar_estado_habitaciones.html', habitaciones=habitaciones)

@app.route('/reservas/extender/<int:id_reserva>', methods=['GET', 'POST'])
def extender_reserva_ruta(id_reserva):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    reserva = database.obtener_reserva(id_reserva)  # Necesitamos esta función

    if request.method == 'POST':
        nueva_fecha_salida = request.form['fecha_salida']
        exito = database.extender_reserva(id_reserva, nueva_fecha_salida)
        if exito:
            return redirect(url_for('lista_reservas'))
        else:
            error = "No se puede extender la reserva, hay conflicto con otra reserva futura."
            return render_template('extender_reserva.html', reserva=reserva, error=error)

    return render_template('extender_reserva.html', reserva=reserva)

@app.route('/modificar_precio', methods=['POST'])
def modificar_precio():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    id_habitacion = request.form['id_habitacion']
    precio_nuevo = request.form['precio_por_noche']
    nuevo_estado = request.form['nuevo_estado']  # <-- obtenemos el nuevo estado

    try:
        precio_nuevo = float(precio_nuevo)
        database.cambiar_precio_y_estado_habitacion(id_habitacion, precio_nuevo, nuevo_estado)
        flash('Precio y estado actualizados correctamente', 'success')
    except ValueError:
        flash('El precio ingresado no es válido', 'error')

    return redirect(url_for('lista_habitaciones'))


if __name__ == '__main__':
    app.run(debug=True)
