from flask import Flask, render_template, request, redirect, url_for, session
import time
import json
import os
from supabase import create_client, Client

# URL de ton image précédente
SUPABASE_URL = "https://yiqpncfhfbltaalhgenp.supabase.co"
# CLÉ de ta dernière image (Publishable key)
SUPABASE_KEY = "sb_publishable_GR_DdAtHA7_DB55cLywtrw_0TlybFWx" 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'shinoza_ultraze_v2'

# Dossiers temporaires pour Vercel
TEMP_USERS = "/tmp/utilisateurs.json"
TEMP_VENTES = "/tmp/ventes.json"

# --- LISTE OFFICIELLE DES ENTREPRISES ---
ENTREPRISES_LISTE = [
    "Restaurant Vinewood", "Burger Shot", "REX Diner + LTD", "Pop Chiken",
    "Unicorn", "Bahamas", "Fête Forraine", "Agence d'évènementiel", "Le Clown",
    "Benny's", "LS Custom", "Garage Paleto", "REX Garage", "Custom Mirror", "Auto Repair 68",
    "Dynasty 8", "LTD Little Seoul", "LTD Groove Street", "Ammunation", "Car Dealer",
    "Taxi", "Psychologue", "Transport et livraison", "Salon de tatouage Aguja", "Salon de tatouage Vespucci"
]

# --- UTILITAIRES ---

def charger_utilisateurs():
    if not os.path.exists(TEMP_USERS):
        return {"admin": {"password": "admin123", "name": "Shinoza", "role": "MASTER", "entreprise": "ADMINISTRATION"}}
    try:
        with open(TEMP_USERS, 'r') as f:
            return json.load(f)
    except:
        return {"admin": {"password": "admin123", "name": "Shinoza", "role": "MASTER", "entreprise": "ADMINISTRATION"}}

def sauvegarder_utilisateurs(users):
    with open(TEMP_USERS, 'w') as f:
        json.dump(users, f, indent=4)

def charger_ventes():
    if not os.path.exists(TEMP_VENTES):
        return []
    try:
        with open(TEMP_VENTES, 'r') as f:
            return json.load(f)
    except:
        return []

def sauvegarder_ventes(ventes):
    with open(TEMP_VENTES, 'w') as f:
        json.dump(ventes, f, indent=4)

@app.context_processor
def inject_globals():
    return dict(entreprises=ENTREPRISES_LISTE)

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
        session['user']['uid'] = u
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
    
    if user_logged.get('role') == "MASTER":
        mes_employes = all_u
    else:
        ent = user_logged.get('entreprise')
        mes_employes = {k: v for k, v in all_u.items() if v.get('entreprise') == ent}
        
    return render_template('utilisateurs.html', all_users=mes_employes)

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user' not in session: return redirect(url_for('login'))
    users = charger_utilisateurs()
    uid = request.form.get('new_username')
    if uid:
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

@app.route('/ventes')
def ventes_page():
    if 'user' not in session: 
        return redirect(url_for('login'))
    
    # On récupère l'entreprise de l'utilisateur connecté
    user_ent = session['user'].get('entreprise')
    
    # 1. Récupérer les ventes de l'entreprise, triées par les plus récentes (id descendant)
    res_ventes = supabase.table("ventes")\
        .select("*")\
        .eq("entreprise", user_ent)\
        .order("id", desc=True)\
        .execute()
    
    # 2. Récupérer le catalogue
    # Si tu veux que le catalogue soit aussi séparé par entreprise, rajoute : .eq("entreprise", user_ent)
    res_cat = supabase.table("catalogue")\
        .select("*")\
        .order("nom")\
        .execute()
    
    return render_template('ventes.html', 
                           ventes=res_ventes.data, 
                           catalogue=res_cat.data,
                           user=session['user'])

@app.route('/add_vente', methods=['POST'])
def add_vente():
    if 'user' not in session: return redirect(url_for('login'))
    ventes = charger_ventes()
    nouvelle_vente = {
        "id": str(int(time.time())),
        "vendeur": session['user']['name'],
        "entreprise": session['user']['entreprise'],
        "article": request.form.get('article'),
        "quantite": int(request.form.get('quantite') or 0),
        "montant_net": float(request.form.get('montant') or 0),
        "date": time.strftime("%d/%m %H:%M")
    }
    ventes.append(nouvelle_vente)
    sauvegarder_ventes(ventes)
    return redirect(url_for('ventes_page'))

@app.route('/salaires')
def salaires_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_ent = session['user'].get('entreprise')
    
    # 1. Grille salariale
    grille = {
        "Recrue": 0.50,
        "Employé": 0.55,
        "Manager": 0.60,
        "Co patron": 0.63,
        "Patron": 0.65
    }

    # 2. Récupérer tous les employés de l'entreprise
    res_users = supabase.table("utilisateurs").select("*").eq("entreprise", user_ent).execute()
    employes = res_users.data
    
    # 3. Récupérer toutes les ventes de l'entreprise
    res_ventes = supabase.table("ventes").select("*").eq("entreprise", user_ent).execute()
    toutes_ventes = res_ventes.data

    # 4. Calculer le salaire pour chaque employé
    liste_salaires = []
    for emp in employes:
        total_ventes_emp = sum(v['montant_net'] for v in toutes_ventes if v['vendeur'] == emp['name'])
        
        grade = emp.get('role', 'Recrue')
        pourcentage = grille.get(grade, 0.50) # 50% par défaut si grade inconnu
        salaire_final = total_ventes_emp * pourcentage
        
        liste_salaires.append({
            "nom": emp['name'],
            "grade": grade,
            "pourcentage": int(pourcentage * 100),
            "chiffre_affaire": total_ventes_emp,
            "salaire_net": salaire_final
        })

    return render_template('salaires.html', salaires=liste_salaires)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Route pour afficher la page Stocks
@app.route('/types-ventes')
def types_ventes_page():
    if 'user' not in session: return redirect(url_for('login'))
    # On récupère tout le catalogue pour l'afficher
    res = supabase.table("catalogue").select("*").order("nom").execute()
    return render_template('type-ventes.html', catalogue=res.data)

# Route pour ajouter un nouvel article au catalogue
@app.route('/add_to_catalog', methods=['POST'])
def add_to_catalog():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Récupération des données du formulaire
    nom = request.form.get('item_name')
    prix = request.form.get('item_price')
    
    if nom and prix:
        try:
            # Enregistrement dans la table "catalogue" de Supabase
            supabase.table("catalogue").insert({
                "nom": nom, 
                "prix": float(prix)
            }).execute()
        except Exception as e:
            print(f"Erreur catalogue: {e}")
            
    return redirect(url_for('ventes_page'))

# Route pour modifier le stock (+ ou -)
@app.route('/update_stock/<nom>/<action>')
def update_stock(nom, action):
    res = supabase.table("catalogue").select("stock").eq("nom", nom).single().execute()
    current_stock = res.data['stock']
    
    new_stock = current_stock + 1 if action == 'add' else current_stock - 1
    if new_stock < 0: new_stock = 0
    
    supabase.table("catalogue").update({"stock": new_stock}).eq("nom", nom).execute()
    return redirect('/types-ventes')
