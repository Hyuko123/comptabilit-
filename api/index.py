from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'shinoza_ultraze_v2'

# Liste complète des entreprises de tes images
entreprises_liste = [
    "Restaurant Vinewood", "Burger Shot", "REX Diner + LTD", "Pop Chiken",
    "Unicorn", "Bahamas", "Fête Forraine", "Agence d'évènementiel", "Le Clown",
    "Benny's", "LS Custom", "Garage Paleto", "REX Garage", "Custom Mirror", "Auto Repair 68",
    "Dynasty 8", "LTD Little Seoul", "LTD Groove Street", "Ammunation", "Car Dealer",
    "Taxi", "Psychologue", "Transport et livraison", "Salon de tatouage Aguja", "Salon de tatouage Vespucci"
]

# Base de données temporaire (se vide au redémarrage Vercel)
users_db = {
    "admin": {"password": "admin123", "name": "Shinoza", "role": "MASTER", "entreprise": "ADMINISTRATION"}
}

@app.context_processor
def inject_user():
    return dict(user=session.get('user'), entreprises=entreprises_liste)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u = request.form.get('username')
    p = request.form.get('password')
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
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('ventes.html')

@app.route('/utilisateurs')
def utilisateurs():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('utilisateurs.html', all_users=users_db)

@app.route('/add_user', methods=['POST'])
def add_user():
    new_u = request.form.get('new_username')
    users_db[new_u] = {
        "password": request.form.get('new_password'),
        "name": request.form.get('new_name'),
        "role": request.form.get('new_role'),
        "entreprise": request.form.get('new_entreprise')
    }
    return redirect(url_for('utilisateurs'))

@app.route('/salaires')
def salaires(): return render_template('salaires.html')

@app.route('/types-ventes')
def types_ventes(): return render_template('stocks.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
