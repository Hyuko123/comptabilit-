from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'shinoza_key_ultraze'

# Liste complète des entreprises pour les menus déroulants
entreprises_liste = [
    "Restaurant Vinewood", "Burger Shot", "REX Diner + LTD", "Pop Chiken",
    "Unicorn", "Bahamas", "Fête Forraine", "Agence d'évènementiel", "Le Clown",
    "Benny's", "LS Custom", "Garage Paleto", "REX Garage", "Custom Mirror", "Auto Repair 68",
    "Dynasty 8", "LTD Little Seoul", "LTD Groove Street", "Ammunation", "Car Dealer",
    "Taxi", "Psychologue", "Transport et livraison", "Salon de tatouage Aguja", "Salon de tatouage Vespucci"
]

users_db = {
    "admin": {"password": "admin123", "name": "Shinoza", "role": "MASTER", "entreprise": "ADMINISTRATION"}
}

@app.context_processor
def inject_vars():
    # Injection sécurisée : si l'utilisateur n'est pas connecté, user = None
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
    # Valeurs par défaut pour éviter le crash "Internal Server Error"
    stats = {'ca': "4.650", 'taxes': "1.628", 'benefice': "465"}
    return render_template('dashboard.html', stats=stats)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
