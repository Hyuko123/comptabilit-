from flask import Flask, render_template, request, redirect, url_for, session
from .database import *

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'ultraze_v2_core_ultra_secret'

# Barème des commissions (Basé sur ton CA personnel)
COMMISSIONS = {
    "Patron": 0.65,
    "Co Patron": 0.63,
    "Manager": 0.60,
    "Employé": 0.55
}

@app.context_processor
def inject_vars():
    user = session.get('user')
    return dict(user=user)

@app.route('/')
def login(): 
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u, p = request.form.get('username'), request.form.get('password')
    users = charger_users()
    if u in users and users[u]['password'] == p:
        session['user'] = users[u]
        session['user']['username'] = u 
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    
    if user['role'] == 'SYSTEM_ADMIN':
        ent_config = charger_config_entreprises()
        return render_template('admin_master.html', entreprises=ent_config)
    
    # Récupération des infos de l'entreprise (Taxes, etc)
    ent_info = charger_config_entreprises().get(user['entreprise'], {"taxe_irs": 15})
    taxe_rate = ent_info.get('taxe_irs', 15) / 100

    # Chiffre d'affaires de l'entreprise uniquement
    ventes = [v for v in charger_ventes() if v['entreprise'] == user['entreprise']]
    ca = sum(v['net'] for v in ventes)
    
    stats = {
        'ca': ca,
        'taxes': int(ca * taxe_rate),
        'benefice': int(ca * (1 - taxe_rate))
    }
    return render_template('dashboard.html', stats=stats)

# --- GESTION DES VENTES ---
@app.route('/ventes')
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    ventes_all = charger_ventes()
    
    # Filtrer par entreprise
    filtrees = [v for v in ventes_all if v['entreprise'] == user['entreprise']]
    
    # Charger les produits autorisés pour cette entreprise
    ent_config = charger_config_entreprises().get(user['entreprise'], {})
    produits = ent_config.get('produits', []) # Liste de dict: [{"nom": "Burger", "prix": 75}, ...]
    
    return render_template('ventes.html', ventes=filtrees, produits=produits)

@app.route('/add_vente', methods=['POST'])
def add_vente():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    ventes_all = charger_ventes()
    
    item_nom = request.form.get('item')
    qty = int(request.form.get('qty', 1))
    vente_id = request.form.get('vente_id') # Présent si modification

    # Chercher le prix dans config_entreprises
    ent_config = charger_config_entreprises().get(user['entreprise'], {})
    produits = ent_config.get('produits', [])
    prix_unitaire = next((p['prix'] for p in produits if p['nom'] == item_nom), 0)
    total_net = prix_unitaire * qty

    if vente_id: # MODIFICATION
        for v in ventes_all:
            if str(v['id']) == str(vente_id) and v['entreprise'] == user['entreprise']:
                v.update({"item": item_nom, "qty": qty, "net": total_net})
                break
    else: # NOUVELLE VENTE
        nouvelle_vente = {
            "id": len(ventes_all) + 1,
            "vendeur": user['name'],
            "entreprise": user['entreprise'],
            "item": item_nom,
            "qty": qty,
            "net": total_net
        }
        ventes_all.append(nouvelle_vente)
    
    sauvegarder_ventes(ventes_all)
    return redirect(url_for('ventes'))

@app.route('/delete_vente/<int:id>')
def delete_vente(id):
    if 'user' not in session: return redirect(url_for('login'))
    v_all = charger_ventes()
    # On ne supprime que si la vente appartient à l'entreprise de l'utilisateur
    v_all = [v for v in v_all if not (v['id'] == id and v['entreprise'] == session['user']['entreprise'])]
    sauvegarder_ventes(v_all)
    return redirect(url_for('ventes'))

# --- GESTION DES EMPLOYÉS (CRÉATION DE COMPTE) ---
@app.route('/utilisateurs')
def utilisateurs():
    if 'user' not in session: return redirect(url_for('login'))
    if session['user']['role'] not in ['Patron', 'Co Patron', 'SYSTEM_ADMIN']:
        return redirect(url_for('dashboard'))
    
    all_users = charger_users()
    mes_employes = {k: v for k, v in all_users.items() if v['entreprise'] == session['user']['entreprise']}
    return render_template('utilisateurs.html', employes=mes_employes)

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user' not in session or session['user']['role'] not in ['Patron', 'Co Patron']:
        return redirect(url_for('login'))
    
    users = charger_users()
    nom_complet = request.form.get('new_name')
    identifiant = nom_complet.lower().replace(" ", "")
    
    # Création du compte employé rattaché à l'entreprise du patron
    users[identifiant] = {
        "password": "123", # Mot de passe par défaut
        "name": nom_complet,
        "role": request.form.get('new_role', 'Employé'),
        "entreprise": session['user']['entreprise'],
        "telephone": "À définir",
        "iban": "À définir",
        "prime": 0,
        "avance": 0
    }
    sauvegarder_users(users)
    return redirect(url_for('utilisateurs'))

# --- CALCUL DES SALAIRES (COMMISSIONS) ---
@app.route('/salaires')
def salaires():
    if 'user' not in session: return redirect(url_for('login'))
    user_session = session['user']
    ent = user_session['entreprise']
    
    users = charger_users()
    ventes_all = charger_ventes()
    liste_salaires = []

    for username, data in users.items():
        if data['entreprise'] == ent:
            # Calcul du CA personnel de cet employé
            v_perso = [v for v in ventes_all if v['vendeur'] == data['name'] and v['entreprise'] == ent]
            ca_p = sum(v['net'] for v in v_perso)
            
            # Récupération du taux selon le barème
            taux = COMMISSIONS.get(data['role'], 0.55)
            
            liste_salaires.append({
                "username": username,
                "name": data['name'],
                "role": data['role'],
                "ca_perso": ca_p,
                "taux": int(taux * 100),
                "salaire_du": int(ca_p * taux),
                "prime": data.get('prime', 0),
                "avance": data.get('avance', 0),
                "telephone": data.get('telephone', ""),
                "iban": data.get('iban', "")
            })
    return render_template('salaires.html', employes=liste_salaires)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
