from flask import Flask, render_template, request, redirect, url_for, session
import database 

app = Flask(__name__)
app.secret_key = 'secret_key'  # Clave secreta para manejar las sesiones

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'admin' in request.form:
            return redirect(url_for('admin_login')) 
        elif 'socio' in request.form:
            return redirect(url_for('socio_login')) 
    return render_template('index.html')

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
            error = "Usuario o contraseña incorrectos"
            return render_template('admin_login.html', error=error)
    
    return render_template('admin_login.html')

@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_panel.html')

if __name__ == "__main__":
    database.create_tables()
    database.create_admin('EDUARDO RAMOS', '12345')
    database.create_admin('JUAN PUCHETA', '12345')
    app.run(debug=True)
