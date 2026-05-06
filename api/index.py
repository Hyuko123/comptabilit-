from flask import Flask, render_template, request, redirect, url_for, session
import time
import json
import os

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'shinoza_ultraze_v2'

# Dossier temporaire pour Vercel
TEMP_USERS = "/tmp/utilisateurs.json"
TEMP_VENTES = "/tmp/ventes.json"

# --- UTILITAIRES DE CHARGEMENT ---

def charger_utilisateurs():
    if not os.path.exists(TEMP_USERS):
        # On crée un fichier de base si rien n'existe
        return {"admin": {"password": "admin123", "name": "Shinoza", "role": "MASTER", "entreprise": "ADMINISTRATION"}}
    with open(TEMP_USERS, 'r') as f:
        return json.load(f)

def sauvegarder_utilisateurs(users):
    with open(TEMP_USERS, 'w') as f:
        json.dump(users, f, indent=4)

def charger_ventes():
    if not os.path.exists(TEMP_VENTES):
        return []
    with open(TEMP_VENTES, 'r') as f:
        return json.load(f)

def sauvegarder_ventes(ventes):
    with open(TEMP_VENTES, 'w') as f:
        json.dump(ventes, f, indent=4)

# --- ROUTES ---

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u = request.form.get('username')
    p = request.form.get('password')
    users = charger_utilisateurs()
    if u in users and users[u]['password'] == p:
        session['user'] = users[u]
        session['user']['uid'] = u # On garde l'ID en session
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    
    user_ent = session['user'].get('entreprise', 'Restaurant Vinewood')
    ventes_all = charger_ventes()
    
    mes_ventes = [v for v in ventes_all if v.get('entreprise') == user_ent]
    ca = sum(v.get('montant_net', 0) for v in mes_ventes)
    
    stats = {
        'ca': ca,
        'taxes': int(ca * 0.15),
        'benefice': int(ca * 0.85),
        'nom_user': session['user'].get('name'),
        'entreprise': user_ent
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/utilisateurs')
def utilisateurs():
    if 'user' not in session: return redirect(url_for('login'))
    
    all_u = charger_utilisateurs()
    user_logged = session['user']
    
    # Filtrage par entreprise
    if user_logged.get('role') == "MASTER":
        mes_employes = all_u
    else:
        ent = user_logged.get('entreprise')
        mes_employes = {k: v for k, v in all_u.items() if v.get('entreprise') == ent}
        
    return render_template('utilisateurs.html', all_users=mes_employes)

@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        uid = request.form.get('new_username')
        users = charger_utilisateurs()
        
        users[uid] = {
            "name": request.form.get('new_name'),
            "password": request.form.get('new_password'),
            "role": request.form.get('new_role'),
            "entreprise": request.form.get('new_entreprise')
        }
        
        sauvegarder_utilisateurs(users)
        return redirect(url_for('utilisateurs'))
    except Exception as e:
        return f"Erreur : {e}", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Indispensable pour Vercel
if __name__ == '__main__':
    app.run(debug=True)
