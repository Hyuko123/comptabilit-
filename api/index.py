from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'ultraze_secret_key' # Nécessaire pour les sessions

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Correction : On vérifie admin / admin123
    if username == "admin" and password == "admin123":
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    else:
        # Si ça rate, on revient au login (tu peux ajouter un message d'erreur ici)
        return redirect(url_for('login_page'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

# Routes pour éviter les erreurs 404 au clic sur les catégories
@app.route('/ventes')
def ventes(): return "<h1>Page Ventes</h1>"

@app.route('/salaires')
def salaires(): return "<h1>Page Salaires</h1>"

@app.route('/utilisateurs')
def utilisateurs(): return "<h1>Page Utilisateurs</h1>"

@app.route('/types-ventes')
def types_ventes(): return "<h1>Types de ventes</h1>"

@app.route('/clotures')
def clotures(): return "<h1>Taxes & Clôtures</h1>"

@app.route('/irs')
def irs(): return "<h1>Avertissement IRS</h1>"

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login_page'))
