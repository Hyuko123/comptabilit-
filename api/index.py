# api/index.py
from flask import Flask, render_template, request, redirect, url_for, session
from .config import PRODUITS_PAR_ENTREPRISE
from .database import charger_ventes, sauvegarder_ventes, charger_users, sauvegarder_users

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'ultraze_v2_core'

@app.context_processor
def inject_vars():
    user = session.get('user')
    produits = PRODUITS_PAR_ENTREPRISE.get(user.get('entreprise'), {}) if user else {}
    return dict(user=user, produits=produits)

@app.route('/')
def login(): return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u, p = request.form.get('username'), request.form.get('password')
    users = charger_users()
    if u in users and users[u]['password'] == p:
        session['user'] = users[u]
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/ventes')
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    ventes_all = charger_ventes()
    filtrees = [v for v in ventes_all if v['entreprise'] == session['user']['entreprise']]
    return render_template('ventes.html', ventes=filtrees)

@app.route('/add_vente', methods=['POST'])
def add_vente():
    if 'user' not in session: return redirect(url_for('login'))
    
    ventes_all = charger_ventes()
    user = session['user']
    item = request.form.get('item')
    qty = int(request.form.get('qty', 1))
    vente_id = request.form.get('vente_id')
    
    prix = PRODUITS_PAR_ENTREPRISE.get(user['entreprise'], {}).get(item, 0)
    total = prix * qty

    if vente_id:
        for v in ventes_all:
            if str(v['id']) == str(vente_id):
                v.update({"item": item, "qty": qty, "net": total})
                break
    else:
        ventes_all.append({
            "id": len(ventes_all) + 1, "vendeur": user['name'],
            "entreprise": user['entreprise'], "item": item, "qty": qty, "net": total
        })
    
    sauvegarder_ventes(ventes_all)
    return redirect(url_for('ventes'))

@app.route('/salaires')
def salaires():
    if 'user' not in session: return redirect(url_for('login'))
    
    ent = session['user']['entreprise']
    users = charger_users()
    ventes_all = charger_ventes()
    liste_salaires = []
    ca_global = 0

    for _, data in users.items():
        if data['entreprise'] == ent:
            v_perso = [v for v in ventes_all if v['vendeur'] == data['name'] and v['entreprise'] == ent]
            ca_p = sum(v['net'] for v in v_perso)
            ca_global += ca_p
            liste_salaires.append({
                **data, "ca_perso": ca_p, "nombre_ventes": len(v_perso)
            })

    return render_template('salaires.html', employes=liste_salaires, ca_total_entreprise=ca_global)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', stats={'ca': "0", 'taxes': "0", 'benefice': "0"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
