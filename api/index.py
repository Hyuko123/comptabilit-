from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'ultraze_secret_key'

# Base de données simulée avec Admin par défaut
users_db = {
    "admin": {"password": "admin123", "name": "Admin", "role": "MASTER", "entreprise": "ADMINISTRATION"}
}

# Données de démonstration pour le Dashboard
stats_demo = {'ca': "4.650", 'taxes': "1.628", 'benefice': "465"}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u, p = request.form.get('username'), request.form.get('password')
    if u in users_db and users_db[u]['password'] == p:
        session['user'] = users_db[u]
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', stats=stats_demo, user=session['user'])

# --- ROUTES DES CATÉGORIES (Évite les erreurs 500) ---

@app.route('/ventes')
def ventes():
    return render_template('ventes.html', user=session.get('user'))

@app.route('/salaires')
def salaires():
    return render_template('salaires.html', user=session.get('user'))

@app.route('/utilisateurs')
def utilisateurs():
    return render_template('utilisateurs.html', all_users=users_db, user=session.get('user'))

@app.route('/types-ventes')
def types_ventes():
    return render_template('types_ventes.html', user=session.get('user'))

@app.route('/clotures')
def clotures():
    return render_template('clotures.html', user=session.get('user'))

@app.route('/irs')
def irs():
    return render_template('irs.html', user=session.get('user'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
