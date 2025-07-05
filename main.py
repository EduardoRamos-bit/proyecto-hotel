from flask import Flask, render_template, request, redirect, url_for, session
import database

app = Flask(__name__)
app.secret_key = 'clave_secreta'

@app.route('/')
def index():
    return redirect(url_for('admin_login'))

# --- LOGIN ADMIN ---
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

# --- PANEL ADMIN ---
@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_panel.html')

# --- LOGOUT ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
