from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Modifie cette ligne :
app = Flask(__name__, template_folder="../templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/ultraze.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELES DE DONNÉES ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='Employe') # Patron, Co Patron, Manager, Employe Intermediaire, Employe
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
    taxe_irs = db.Column(db.Float) # 20% calculé auto

# --- GESTION CONNEXION ---

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Identifiants incorrects')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- SYSTÈME DE VENTES & STOCK ---

@app.route('/ventes', methods=['GET', 'POST'])
@login_required
def ventes():
    produits = Product.query.all()
    if request.method == 'POST':
        p_id = request.form.get('produit_id')
        produit = Product.query.get(p_id)
        
        if produit and produit.quantite_stock > 0:
            produit.quantite_stock -= 1
            taxe = produit.prix_vente * 0.20 # IRS 20%
            nouvelle_vente = Sale(produit_id=p_id, vendeur_id=current_user.id, montant=produit.prix_vente, taxe_irs=taxe)
            db.session.add(nouvelle_vente)
            db.session.commit()
            flash(f'Vente réussie ! Taxe IRS provisionnée : {taxe}€')
        else:
            flash('Erreur : Stock insuffisant !')
            
    return render_template('ventes.html', produits=produits)

# --- PANEL ADMIN (CRÉATION COMPTES) ---

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    # Sécurité : Uniquement Patron et Co Patron
    if current_user.role not in ['Patron', 'Co Patron']:
        return "Accès Interdit", 403
    
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        new_user = User(
            username=request.form['username'],
            password=hashed_pw,
            role=request.form['role'],
            commission_pct=float(request.form['commission'])
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Nouvel employé ajouté !')
        
    users = User.query.all()
    return render_template('admin.html', users=users)

