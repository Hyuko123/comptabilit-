from flask import Flask, render_template, request, redirect, url_for, session
import time
import json
import os

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'shinoza_ultraze_v2'

# Dossiers temporaires obligatoires pour Vercel
TEMP_USERS = "/tmp/utilisateurs.json"
TEMP_VENTES = "/tmp/ventes.json"

# --- FONCTIONS DE GESTION DES DONNÉES ---

def charger_utilisateurs():
    if not os.path.exists(TEMP_USERS):
        # Admin par défaut si le fichier n'existe pas encore
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

# --- ROUTES DE NAVIGATION ---

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
        session['user']['uid'] = u
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    ventes_all = charger_ventes()
    mes_ventes = [v for v in ventes_all if v.get('entreprise') == user_ent]
    ca = sum(v.get('montant_net', 0) for v in mes_ventes)
    
    stats = {'ca': ca, 'taxes': int(ca * 0.15), 'benefice': int(ca * 0.85),
             'nom_user': session['user'].get('name'), 'entreprise': user_ent}
    return render_template('dashboard.html', stats=stats)

# --- GESTION DES UTILISATEURS ---

@app.route('/utilisateurs')
def utilisateurs():
    if 'user' not in session: return redirect(url_for('login'))
    all_u = charger_utilisateurs()
    # On affiche tout pour le MASTER, sinon uniquement son entreprise
    if session['user'].get('role') == "MASTER":
        mes_employes = all_u
    else:
        ent = session['user'].get('entreprise')
        mes_employes = {k: v for k, v in all_u.items() if v.get('entreprise') == ent}
    return render_template('utilisateurs.html', all_users=mes_employes)

@app.route('/add_user', methods=['POST'])
def add_user():
    users = charger_utilisateurs()
    uid = request.form.get('new_username')
    users[uid] = {
        "name": request.form.get('new_name'),
        "password": request.form.get('new_password'),
        "role": request.form.get('new_role'),
        "entreprise": request.form.get('new_entreprise')
    }
    sauvegarder_utilisateurs(users)
    return redirect(url_for('utilisateurs'))

@app.route('/delete_user/<uid>')
def delete_user(uid):
    if 'user' not in session: return redirect(url_for('login'))
    users = charger_utilisateurs()
    if uid in users:
        del users[uid]
        sauvegarder_utilisateurs(users)
    return redirect(url_for('utilisateurs'))

# --- AUTRES PAGES (Éviter le "Not Found") ---

@app.route('/ventes')
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    mes_ventes = [v for v in charger_ventes() if v.get('entreprise') == session['user'].get('entreprise')]
    return render_template('ventes.html', ventes=mes_ventes)

@app.route('/salaires')
def salaires():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('salaires.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
