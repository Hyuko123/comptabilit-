from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'ultraze_master_key'

# Simulation de base de données des entreprises et taxes
# Dans un vrai projet, ceci serait dans ta base de données
entreprises_db = {
    "Rex Diner + LTD": {"taxes_irs": 35, "grades": {"Patron": 65, "Co Patron": 63, "Manager": 60, "Employé": 55}},
    "Ultraze Corp": {"taxes_irs": 20, "grades": {"Patron": 100}}
}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u = request.form.get('username')
    p = request.form.get('password')
    
    # ACCÈS MASTER ADMIN (Shinoza)
    if u == "admin" and p == "admin123":
        session['user'] = {'name': 'Shinoza', 'role': 'MASTER', 'entreprise': 'ADMINISTRATION'}
        return redirect(url_for('admin_panel'))
    
    # ACCÈS ENTREPRISE (Exemple)
    if u == "rex" and p == "rex123":
        session['user'] = {'name': 'Amare', 'role': 'Patron', 'entreprise': 'Rex Diner + LTD'}
        return redirect(url_for('dashboard'))

    return redirect(url_for('login'))

# --- PANEL ADMIN UNIQUE (ADMIN ONLY) ---
@app.route('/admin-master')
def admin_panel():
    if session.get('user', {}).get('role') != 'MASTER':
        return "Accès interdit", 403
    return render_template('admin_master.html', entreprises=entreprises_db)

# --- ROUTES CLASSIQUES ---
@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    # On récupère les taxes spécifiques à l'entreprise de l'utilisateur
    ent = session['user']['entreprise']
    config = entreprises_db.get(ent, {"taxes_irs": 0, "grades": {}})
    return render_template('dashboard.html', user=session['user'], config=config)

@app.route('/ventes')
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('ventes.html', user=session['user'])

@app.route('/utilisateurs')
def utilisateurs():
    if 'user' not in session: return redirect(url_for('login'))
    # Si c'est l'admin, il voit tout. Si c'est un patron, il ne voit que ses employés.
    return render_template('utilisateurs.html', user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
