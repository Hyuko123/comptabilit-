from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'shinoza_ultraze_v2_key'

# Simulation de base de données (se réinitialise au redémarrage sur Vercel)
# Pour une vraie persistance, il faudra lier une DB externe (ex: Supabase)
users_db = {
    "admin": {"password": "admin123", "name": "Shinoza", "role": "MASTER", "entreprise": "ADMINISTRATION"}
}

entreprises = [
    "Rex Diner + LTD", "Pops Diner", "Up-n-Atom", "Burgershot", 
    "Wigwam", "Bean Machine", "Yellow Jack", "Vanilla Unicorn", "Bahama Mamas"
]

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u = request.form.get('username')
    p = request.form.get('password')
    
    if u in users_db and users_db[u]['password'] == p:
        session['user'] = users_db[u]
        session['user']['username'] = u
        if users_db[u]['role'] == 'MASTER':
            return redirect(url_for('dashboard')) # Ou admin_master
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/utilisateurs')
def utilisateurs():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('utilisateurs.html', user=session['user'], entreprises=entreprises, all_users=users_db)

@app.route('/add_user', methods=['POST'])
def add_user():
    # Seul l'admin ou un Patron peut créer
    new_u = request.form.get('new_username')
    users_db[new_u] = {
        "password": request.form.get('new_password'),
        "name": request.form.get('new_name'),
        "role": request.form.get('new_role'),
        "entreprise": request.form.get('new_entreprise')
    }
    return redirect(url_for('utilisateurs'))

@app.route('/ventes')
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('ventes.html', user=session['user'])

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
