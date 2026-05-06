from flask import Flask, render_template, request, redirect, url_for, session
import os
# Import relatif pour Vercel
from .database import charger_ventes, sauvegarder_ventes, charger_users, sauvegarder_users, charger_config_entreprises

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'ultraze_v2_core_key'

# Barème des commissions (Ton barème demandé)
COMMISSIONS = {
    "Patron": 0.65,
    "Co Patron": 0.63,
    "Manager": 0.60,
    "Employé": 0.55
}

# ... (le reste du code que je t'ai donné précédemment)

@app.context_processor
def inject_vars():
    return dict(user=session.get('user'))

@app.route('/')
def login(): return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u, p = request.form.get('username'), request.form.get('password')
    users = charger_users()
    if u in users and users[u]['password'] == p:
        session['user'] = users[u]
        session['user']['id_login'] = u
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ... (tes imports)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    
    if user.get('role') == 'SYSTEM_ADMIN':
        return render_template('admin_master.html', entreprises=charger_config_entreprises())
    
    # On utilise .get() pour éviter le crash si l'entreprise n'existe pas
    ventes_all = charger_ventes() or []
    ventes = [v for v in ventes_all if v.get('entreprise') == user.get('entreprise')]
    
    ca = sum(v.get('net', 0) for v in ventes)
    
    # Récupération de la taxe configurée
    config = charger_config_entreprises().get(user.get('entreprise'), {})
    taux_irs = config.get('taxe_irs', 15) # 15% par défaut
    
    taxe = int(ca * (taux_irs / 100))
    return render_template('dashboard.html', stats={'ca': ca, 'taxes': taxe, 'benefice': ca - taxe})

# ... (le reste de tes routes)

@app.route('/ventes')
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    v_all = charger_ventes()
    mes_ventes = [v for v in v_all if v['entreprise'] == user['entreprise']]
    produits = charger_config_entreprises().get(user['entreprise'], {}).get('produits', [])
    return render_template('ventes.html', ventes=mes_ventes, produits=produits)

@app.route('/add_vente', methods=['POST'])
def add_vente():
    if 'user' not in session: return redirect(url_for('login'))
    v_all = charger_ventes()
    user = session['user']
    
    item_nom = request.form.get('item')
    qty = int(request.form.get('qty', 1))
    
    # Calcul prix auto
    prods = charger_config_entreprises().get(user['entreprise'], {}).get('produits', [])
    prix = next((p['prix'] for p in prods if p['nom'] == item_nom), 0)
    
    v_all.append({
        "id": len(v_all) + 1,
        "vendeur": user['name'],
        "entreprise": user['entreprise'],
        "item": item_nom,
        "qty": qty,
        "net": prix * qty
    })
    sauvegarder_ventes(v_all)
    return redirect(url_for('ventes'))

@app.route('/salaires')
def salaires():
    if 'user' not in session: return redirect(url_for('login'))
    ent = session['user']['entreprise']
    users = charger_users()
    ventes = charger_ventes()
    
    tableau = []
    for uid, data in users.items():
        if data['entreprise'] == ent:
            ca_p = sum(v['net'] for v in ventes if v['vendeur'] == data['name'] and v['entreprise'] == ent)
            taux = COMMISSIONS.get(data['role'], 0.55)
            tableau.append({
                **data, "ca_perso": ca_p, "taux": int(taux*100), "salaire_du": int(ca_p * taux)
            })
    return render_template('salaires.html', employes=tableau)

@app.route('/utilisateurs')
def utilisateurs():
    if 'user' not in session: return redirect(url_for('login'))
    all_u = charger_users()
    # On ne voit que les gens de son entreprise
    mes_employes = {k: v for k, v in all_u.items() if v['entreprise'] == session['user']['entreprise']}
    return render_template('utilisateurs.html', employes=mes_employes)

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user' not in session or session['user']['role'] not in ['Patron', 'Co Patron', 'SYSTEM_ADMIN']:
        return redirect(url_for('dashboard'))
    
    users = charger_users()
    nom = request.form.get('new_name')
    uid = nom.lower().replace(" ", "")
    
    users[uid] = {
        "password": "123",
        "name": nom,
        "role": request.form.get('new_role', 'Employé'),
        "entreprise": session['user']['entreprise'],
        "telephone": "N/A", "iban": "N/A", "prime": 0, "avance": 0
    }
    sauvegarder_users(users)
    return redirect(url_for('utilisateurs'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
