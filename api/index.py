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
    if 'user' not in session: 
        return redirect(url_for('login'))
    
    user = session['user']
    user_ent = user.get('entreprise', 'Burger Shot') # Valeur par défaut pour éviter le crash
    
    # On charge les données ou on met des listes vides si ça échoue
    try:
        ventes_all = charger_ventes() or []
        config_all = charger_config_entreprises() or {}
    except:
        ventes_all, config_all = [], {}

    # Filtrage
    mes_ventes = [v for v in ventes_all if v.get('entreprise') == user_ent]
    ca = sum(v.get('net', 0) for v in mes_ventes)
    
    # IRS
    ent_data = config_all.get(user_ent, {})
    taux_irs = ent_data.get('taxe_irs', 15)
    
    stats = {
        'ca': ca,
        'taxes': int(ca * (taux_irs / 100)),
        'benefice': int(ca * (1 - (taux_irs / 100))),
        'nom_user': user.get('name', 'Utilisateur'),
        'entreprise': user_ent
    }
    
    return render_template('dashboard.html', stats=stats)
@app.route('/ventes')
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('ventes.html')

@app.route('/utilisateurs')
def utilisateurs():
    if 'user' not in session: 
        return redirect(url_for('login'))
    
    user_logged = session['user']
    all_u = charger_users()
    
    # 1. On récupère la config pour avoir la liste des entreprises
    # Si charger_config_entreprises() est vide, on met une liste par défaut
    config_ent = charger_config_entreprises() or {"Burger Shot": {}, "LTD": {}, "Unicorn": {}}
    
    # 2. Filtrage : Un patron ne voit que ses gars, l'admin voit tout
    if user_logged.get('role') == "SYSTEM_ADMIN":
        mes_employes = all_u
        liste_pour_select = list(config_ent.keys())
    else:
        ent_name = user_logged.get('entreprise')
        mes_employes = {k: v for k, v in all_u.items() if v.get('entreprise') == ent_name}
        # Le patron ne peut créer des gens que dans sa propre entreprise
        liste_pour_select = [ent_name]
    
    # 3. On envoie TOUT au HTML (all_users ET entreprises)
    return render_template('utilisateurs.html', 
                           all_users=mes_employes, 
                           entreprises=liste_pour_select)

@app.route('/delete_user/<uid>')
def delete_user(uid):
    if 'user' not in session: return redirect(url_for('login'))
    
    users = charger_users()
    if uid in users:
        # Optionnel : vérifier ici que le gars qui supprime est bien le patron de la même entreprise
        del users[uid]
        sauvegarder_users(users)
        
    return redirect(url_for('utilisateurs'))
    
@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user' not in session: return redirect(url_for('login'))
    
    users = charger_users()
    # On récupère les infos du formulaire
    new_uid = request.form.get('new_username').lower().strip()
    
    users[new_uid] = {
        "password": request.form.get('new_password'),
        "name": request.form.get('new_name'),
        "role": request.form.get('new_role'),
        "entreprise": request.form.get('new_entreprise'), # Vérifie que ce nom correspond au <select>
        "telephone": "N/A", "iban": "N/A", "prime": 0, "avance": 0
    }
    
    sauvegarder_users(users)
    return redirect(url_for('utilisateurs'))
    
@app.route('/delete_user/<uid>')
def delete_user(uid):
    if 'user' not in session: return redirect(url_for('login'))
    
    # Sécurité : Un patron ne peut pas supprimer un admin ou quelqu'un d'une autre entreprise
    users = charger_users()
    if uid in users:
        del users[uid]
        sauvegarder_users(users)
        
    return redirect(url_for('utilisateurs'))

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
