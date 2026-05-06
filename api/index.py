from flask import Flask, render_template, request, redirect, url_for

# On précise le dossier des templates car il est en dehors du dossier api/
app = Flask(__name__, template_folder='../templates')

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    # Simulation de connexion simple
    username = request.form.get('username')
    password = request.form.get('password')
    if username == "admin" and password == "admin":
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/ventes')
def ventes():
    return "<h1>Page Ventes</h1><p>En construction...</p>"

@app.route('/salaires')
def salaires():
    return "<h1>Page Salaires</h1><p>En construction...</p>"

@app.route('/utilisateurs')
def utilisateurs():
    return "<h1>Page Utilisateurs</h1><p>En construction...</p>"

@app.route('/types-ventes')
def types_ventes():
    return "<h1>Types de ventes</h1>"

@app.route('/clotures')
def clotures():
    return "<h1>Taxes & Clôtures</h1>"

@app.route('/irs')
def irs():
    return "<h1>Avertissement IRS</h1>"

# Pour Vercel
app.debug = True
