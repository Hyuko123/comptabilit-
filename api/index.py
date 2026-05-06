from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'ultraze_v2_core'

# Configuration des produits par entreprise
# Tu peux ajouter toutes tes entreprises et leurs articles ici
PRODUITS_PAR_ENTREPRISE = {
    "Burger Shot": {
        "Menu Burger": 75,
        "Frites": 20,
        "Soda": 15
    },
    "Unicorn": {
        "Entrée Club": 100,
        "Bouteille Champagne": 500,
        "Cocktail": 50
    },
    "LTD Little Seoul": {
        "Sachet de chips": 10,
        "Eau": 5,
        "Barre chocolatée": 8
    },
    "ADMINISTRATION": {
        "Service Admin": 0,
        "Licence": 1000
    }
}

# Admin par défaut
users_db = {
    "admin": {"password": "admin123", "name": "Admin", "role": "MASTER", "entreprise": "ADMINISTRATION"},
    "shinoza": {"password": "123", "name": "Shinoza", "role": "BOSS", "entreprise": "Burger Shot"}
}

# On filtre les ventes par entreprise pour que personne ne voie les ventes des autres
ventes_db = []

@app.context_processor
def inject_vars():
    user = session.get('user')
    # On récupère les produits spécifiques à l'entreprise de l'utilisateur
    produits = {}
    if user:
        entreprise = user.get('entreprise')
        produits = PRODUITS_PAR_ENTREPRISE.get(entreprise, {})
    
    return dict(user=user, produits=produits)

@app.route('/')
def login(): return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u, p = request.form.get('username'), request.form.get('password')
    if u in users_db and users_db[u]['password'] == p:
        session['user'] = users_db[u]
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/ventes')
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    # On ne montre que les ventes de l'entreprise de l'utilisateur
    entreprise_user = session['user']['entreprise']
    ventes_filtrees = [v for v in ventes_db if v['entreprise'] == entreprise_user]
    return render_template('ventes.html', ventes=ventes_filtrees)

@app.route('/add_vente', methods=['POST'])
def add_vente():
    if 'user' not in session: return redirect(url_for('login'))
    
    user = session['user']
    entreprise = user['entreprise']
    item = request.form.get('item')
    qty = int(request.form.get('qty', 1))
    
    # Récupération du prix spécifique à l'entreprise
    prix_unitaire = PRODUITS_PAR_ENTREPRISE.get(entreprise, {}).get(item, 0)
    total_net = prix_unitaire * qty
    
    nouvelle_vente = {
        "id": len(ventes_db) + 1,
        "vendeur": user['name'],
        "entreprise": entreprise, # On stocke l'entreprise pour le filtrage
        "item": item,
        "qty": qty,
        "net": total_net
    }
    
    ventes_db.append(nouvelle_vente)
    return redirect(url_for('ventes'))

@app.route('/delete_vente/<int:vente_id>')
def delete_vente(vente_id):
    global ventes_db
    ventes_db = [v for v in ventes_db if v['id'] != vente_id]
    return redirect(url_for('ventes'))

# Les autres routes restent identiques...
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
