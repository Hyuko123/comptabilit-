from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'ultraze_v2_core'

# Liste des entreprises
entreprises_liste = ["Restaurant Vinewood", "Burger Shot", "REX Diner + LTD", "Pop Chiken", "Unicorn", "Bahamas", "Benny's", "LS Custom", "Dynasty 8", "LTD Little Seoul", "Ammunation", "Taxi"]

# Admin par défaut
users_db = {
    "admin": {"password": "admin123", "name": "Admin", "role": "MASTER", "entreprise": "ADMINISTRATION"}
}

@app.context_processor
def inject_vars():
    return dict(user=session.get('user'), entreprises=entreprises_liste)

@app.route('/')
def login(): return render_template('login.html')

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
    return render_template('dashboard.html', stats={'ca': "4.650", 'taxes': "1.628", 'benefice': "465"})

@app.route('/ventes')
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    historique = [{"vendeur": "Admin", "item": "Menu Burger", "qty": 2, "total": 150, "net": 135}]
    return render_template('ventes.html', ventes=historique)

@app.route('/salaires')
def salaires(): return render_template('salaires.html')

@app.route('/utilisateurs')
def utilisateurs(): return render_template('utilisateurs.html', all_users=users_db)

@app.route('/types-ventes')
def types_ventes(): return render_template('stocks.html')

@app.route('/clotures')
def clotures(): return render_template('clotures.html')

@app.route('/irs')
def irs(): return render_template('irs.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
