from flask import Flask, render_template, request, redirect, url_for, session
from .database import *

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'ultraze_v2_core_ultra_secret'

# Barème des commissions
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
def login(): return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u, p = request.form.get('username'), request.form.get('password')
    users = charger_users()
    if u in users and users[u]['password'] == p:
        session['user'] = users[u]
        session['user']['username'] = u # On garde l'ID pour les modifs
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    
    if user['role'] == 'SYSTEM_ADMIN':
        ent_config = charger_config_entreprises()
        return render_template('admin_master.html', entreprises=ent_config)
    
    # Calcul stats entreprise
    ventes = [v for v in charger_ventes() if v['entreprise'] == user['entreprise']]
    ca = sum(v['net'] for v in ventes)
    return render_template('dashboard.html', stats={'ca': ca, 'taxes': int(ca*0.15), 'benefice': int(ca*0.85)})

@app.route('/ventes')
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    ventes_all = charger_ventes()
    filtrees = [v for v in ventes_all if v['entreprise'] == session['user']['entreprise']]
    # On passe aussi la liste des produits pour le formulaire
    ent_config = charger_config_entreprises().get(session['user']['entreprise'], {})
    produits = ent_config.get('produits', [])
    return render_template('ventes.html', ventes=filtrees, produits=produits)

@app.route('/add_vente', methods=['POST'])
def add_vente():
    if 'user' not in session: return redirect(url_for('login'))
    v_all = charger_ventes()
    # Logique d'ajout (similaire à ton code précédent mais avec sauvegarde JSON)
    # ... (récupération form)
    # v_all.append(nouvelle_vente)
    sauvegarder_ventes(v_all)
    return redirect(url_for('ventes'))

@app.route('/salaires')
def salaires():
    if 'user' not in session: return redirect(url_for('login'))
    ent = session['user']['entreprise']
    users = charger_users()
    ventes_all = charger_ventes()
    liste_salaires = []

    for username, data in users.items():
        if data['entreprise'] == ent:
            v_perso = [v for v in ventes_all if v['vendeur'] == data['name'] and v['entreprise'] == ent]
            ca_p = sum(v['net'] for v in v_perso)
            taux = COMMISSIONS.get(data['role'], 0.55)
            
            liste_salaires.append({
                **data,
                "ca_perso": ca_p,
                "taux": taux * 100,
                "salaire_du": int(ca_p * taux)
            })
    return render_template('salaires.html', employes=liste_salaires)

@app.route('/utilisateurs')
def utilisateurs():
    if 'user' not in session: return redirect(url_for('login'))
    # Seul un patron ou admin peut voir ça
    if session['user']['role'] not in ['Patron', 'Co Patron', 'SYSTEM_ADMIN']:
        return redirect(url_for('dashboard'))
    
    all_users = charger_users()
    # Filtrer les utilisateurs de l'entreprise uniquement
    mes_employes = {k: v for k, v in all_users.items() if v['entreprise'] == session['user']['entreprise']}
    return render_template('utilisateurs.html', employes=mes_employes)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
