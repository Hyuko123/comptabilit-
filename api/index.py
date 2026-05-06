from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'shinoza_ultraze_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ultraze.db'
db = SQLAlchemy(app)

# --- MODÈLES DE DONNÉES ---
class Entreprise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20)) # Patron, Co-Patron, Manager, Employé
    entreprise_id = db.Column(db.Integer, db.ForeignKey('entreprise.id'))

# --- ROUTES DE CONNEXION ---
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u = request.form.get('username')
    p = request.form.get('password')
    
    # Sécurité : admin/admin123 n'est pas écrit dans le HTML mais géré ici
    if u == "admin" and p == "admin123":
        session['user'] = {'username': 'Shinoza', 'role': 'Admin Global'}
        return redirect(url_for('dashboard'))
    
    # Logique pour les autres utilisateurs en base de données ici...
    return redirect(url_for('login'))

# --- NAVIGATION DASHBOARD ---
@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/ventes')
def ventes():
    return render_template('ventes.html') # Tu devras créer ce fichier

@app.route('/salaires')
def salaires():
    return render_template('salaires.html') # Basé sur ton image

@app.route('/utilisateurs')
def utilisateurs():
    return render_template('utilisateurs.html') # Basé sur ton image

@app.route('/stocks')
def stocks():
    return render_template('stocks.html')

@app.route('/clotures')
def clotures():
    return render_template('clotures.html')

@app.route('/irs')
def irs():
    return render_template('irs.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Crée la base de données
    app.run(debug=True)
