import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

# --- CONFIGURATION INITIALE ---
app = Flask(__name__, template_folder="../templates")
app.secret_key = 'ultraze_secret_key_v2' 
app.instance_path = "/tmp" 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/ultraze.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELES DE DONNÉES ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='Employe')
    salaire_fixe = db.Column(db.Float, default=1200.0)
    commission_pct = db.Column(db.Float, default=5.0)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prix_vente = db.Column(db.Float, nullable=False)
    quantite_stock = db.Column(db.Integer, default=0)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    vendeur_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    montant = db.Column(db.Float)
    taxe_irs = db.Column(db.Float) 

# --- INITIALISATION DE LA BASE (Le bloc que tu attendais) ---
with app.app_context():
    db.create_all()
    # Création du compte Patron par défaut si la base est vide
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin', 
            password=generate_password_hash('admin123'), 
            role='Patron'
        )
        db.session.add(admin)
        db.session.commit()

# --- GESTION CONNEXION ---
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---

@app.route('/')
@login_required
def index():
    # Calculs pour les statistiques du Dashboard
    ca_brut = db.session.query(func.sum(Sale.montant)).scalar() or 0
    total_taxes = db.session.query(func.sum(Sale.taxe_irs)).scalar() or 0
    ca_net = ca_brut - total_taxes
    
    total_commissions = 0
    ventes_liste = Sale.query.all()
    for v in ventes_liste:
        vendeur = User.query.get(v.vendeur_id)
        if vendeur:
            total_commissions += (v.montant * (vendeur.commission_pct / 100))

    return render_template('dashboard.html', 
                           ca_net=ca_net, 
                           taxes=total_taxes, 
                           salaires=total_commissions,
                           benefice=ca_net - total_commissions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('index'))
        flash('Identifiants incorrects')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/ventes')
@login_required # Si tu utilises Flask-Login
def ventes():
    # Ici tu récupères tes données
    return render_template('ventes.html')

@app.route('/salaires')
def salaires():
    return render_template('salaires.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if current_user.role not in ['Patron', 'Co Patron']:
        return "Accès Interdit", 403
    
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form.get('password'))
        new_user = User(
            username=request.form.get('username'),
            password=hashed_pw,
            role=request.form.get('role'),
            commission_pct=float(request.form.get('commission', 5.0))
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Nouvel employé ajouté !')
        
    users = User.query.all()
    return render_template('admin.html', users=users)

# Requis pour Vercel
app = app
