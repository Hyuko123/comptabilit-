from flask import Flask, render_template, request, redirect, url_for, session
from config import PRODUITS_PAR_ENTREPRISE # Tes prix statiques
# On importe nos nouvelles fonctions de sauvegarde
from database import charger_ventes, sauvegarder_ventes, charger_users

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'ultraze_v2_core'

# On garde uniquement la base des ventes en mémoire ici (ou on peut aussi la déplacer)
ventes_db = []

@app.context_processor
def inject_vars():
    user = session.get('user')
    produits = {}
    if user:
        entreprise = user.get('entreprise')
        produits = PRODUITS_PAR_ENTREPRISE.get(entreprise, {})
    return dict(user=user, produits=produits)

@app.route('/')
def login(): 
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u, p = request.form.get('username'), request.form.get('password')
    # Utilisation de USERS_DB importé
    if u in USERS_DB and USERS_DB[u]['password'] == p:
        session['user'] = USERS_DB[u]
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# --- SECTION VENTES ---
@app.route('/ventes')
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    entreprise_user = session['user']['entreprise']
    ventes_filtrees = [v for v in ventes_db if v['entreprise'] == entreprise_user]
    return render_template('ventes.html', ventes=ventes_filtrees)

@app.route('/add_vente', methods=['POST'])
def add_vente():
    if 'user' not in session: return redirect(url_for('login'))
    
    vente_id = request.form.get('vente_id')
    user = session['user']
    entreprise = user['entreprise']
    item = request.form.get('item')
    qty = int(request.form.get('qty', 1))
    
    prix_unitaire = PRODUITS_PAR_ENTREPRISE.get(entreprise, {}).get(item, 0)
    total_net = prix_unitaire * qty

    if vente_id:
        for v in ventes_db:
            if str(v['id']) == str(vente_id):
                v['item'], v['qty'], v['net'] = item, qty, total_net
                break
    else:
        ventes_db.append({
            "id": len(ventes_db) + 1,
            "vendeur": user['name'],
            "entreprise": entreprise,
            "item": item,
            "qty": qty,
            "net": total_net
        })
    return redirect(url_for('ventes'))

@app.route('/delete_vente/<int:vente_id>')
def delete_vente(vente_id):
    global ventes_db
    ventes_db = [v for v in ventes_db if v['id'] != vente_id]
    return redirect(url_for('ventes'))

# --- SECTION SALAIRES ---
@app.route('/salaires')
def salaires():
    if 'user' not in session: return redirect(url_for('login'))
    
    entreprise_actuelle = session['user']['entreprise']
    liste_salaires = []
    ca_global_entreprise = 0

    for username, data in USERS_DB.items():
        if data['entreprise'] == entreprise_actuelle:
            ventes_perso = [v for v in ventes_db if v['vendeur'] == data['name'] and v['entreprise'] == entreprise_actuelle]
            ca_perso = sum(v['net'] for v in ventes_perso)
            ca_global_entreprise += ca_perso

            liste_salaires.append({
                "nom": data['name'],
                "role": data['role'],
                "taux": data.get('taux', 55),
                "ca_perso": ca_perso,
                "nombre_ventes": len(ventes_perso),
                "prime": data.get('prime', 0),
                "avance": data.get('avance', 0),
                "telephone": data.get('telephone', "N/A"),
                "iban": data.get('iban', "N/A"),
                "paye": False
            })

    return render_template('salaires.html', employes=liste_salaires, ca_total_entreprise=ca_global_entreprise)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', stats={'ca': "0", 'taxes': "0", 'benefice': "0"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
