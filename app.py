from flask import Flask, render_template, request, redirect, url_for, session
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
@app.route('/reservar/<int:id_cliente>', methods=['GET', 'POST'])
def reservar_habitacion(id_cliente):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    habitaciones = database.listar_habitaciones_disponibles()

    if request.method == 'POST':
        id_habitacion = request.form['habitacion']
        fecha_entrada = request.form['fecha_entrada']
        fecha_salida = request.form['fecha_salida']

        exito = database.reservar_habitacion(id_cliente, id_habitacion, fecha_entrada, fecha_salida)
        if exito:
            return redirect(url_for('lista_reservas'))
        else:
            return render_template('reservar_habitacion.html', habitaciones=habitaciones, error="Habitación no disponible")

    return render_template('reservar_habitacion.html', habitaciones=habitaciones)

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

if __name__ == '__main__':
    app.run(debug=True)
