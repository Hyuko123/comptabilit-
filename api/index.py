from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'ultraze_admin_v2_key'

# Liste des entreprises (extraite de tes screens)
entreprises_liste = [
    "Restaurant Vinewood", "Burger Shot", "REX Diner + LTD", "Pop Chiken",
    "Unicorn", "Bahamas", "Fête Forraine", "Agence d'évènementiel", "Le Clown",
    "Benny's", "LS Custom", "Garage Paleto", "REX Garage", "Custom Mirror", "Auto Repair 68",
    "Dynasty 8", "LTD Little Seoul", "LTD Groove Street", "Ammunation", "Car Dealer",
    "Taxi", "Psychologue", "Transport et livraison", "Salon de tatouage Aguja", "Salon de tatouage Vespucci"
]

# Utilisateur Admin par défaut
users_db = {
    "admin": {"password": "admin123", "name": "Admin", "role": "MASTER", "entreprise": "ADMINISTRATION"}
}

@app.context_processor
def inject_vars():
    return dict(user=session.get('user'), entreprises=entreprises_liste)

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
    stats = {'ca': "4.650", 'taxes': "1.628", 'benefice': "465"}
    return render_template('dashboard.html', stats=stats)

@app.route('/ventes')
def ventes(): return render_template('ventes.html')

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
