from flask import Flask, render_template, request, redirect, url_for, session
import time
from supabase import create_client, Client
from datetime import datetime

# --- CONFIGURATION ---
SUPABASE_URL = "https://yiqpncfhfbltaalhgenp.supabase.co"
SUPABASE_KEY = "sb_publishable_GR_DdAtHA7_DB55cLywtrw_0TlybFWx"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'shinoza_ultraze_v2'

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True

ENTREPRISES_LISTE = [
    "Restaurant Vinewood", "Burger Shot", "REX Diner + LTD", "Pop Chiken",
    "Unicorn", "Bahamas", "Fête Forraine", "Agence d'évènementiel", "Le Clown",
    "Benny's", "LS Custom", "Garage Paleto", "REX Garage", "Custom Mirror", "Auto Repair 68",
    "Dynasty 8", "LTD Little Seoul", "LTD Groove Street", "Ammunation", "Car Dealer",
    "Taxi", "Psychologue", "Transport et livraison", "Salon de tatouage Aguja", "Salon de tatouage Vespucci"
]

@app.context_processor
def inject_globals():
    return dict(entreprises=ENTREPRISES_LISTE)

# --- AUTHENTIFICATION ---

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u = request.form.get('username')
    p = request.form.get('password')
    try:
        res = supabase.table("utilisateurs").select("*").eq("username", u).execute()
        if res.data and len(res.data) > 0:
            user_data = res.data[0]
            if str(user_data.get('password')) == str(p):
                session['user'] = user_data
                return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    except Exception as e:
        return f"Erreur de connexion : {e}", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Dans ton api/index.py
@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user' not in session: return redirect(url_for('login'))
    
    # Récupération des données du formulaire (doit matcher avec 'name' dans le HTML)
    username = request.form.get('username')
    name = request.form.get('name')
    password = request.form.get('password')
    role = request.form.get('role')
    entreprise = request.form.get('entreprise')
    
    if username and name and password:
        try:
            supabase.table("utilisateurs").insert({
                "username": username,
                "name": name,
                "password": password,
                "role": role,
                "entreprise": entreprise
            }).execute()
        except Exception as e:
            print(f"Erreur Supabase Insertion : {e}")
            return f"Erreur lors de l'insertion : {e}", 500
            
    return redirect(url_for('utilisateurs'))

@app.route('/dashboard')
def dashboard():
    # 1. Sécurité Session
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_ent = session['user'].get('entreprise', 'Inconnue')
    user_name = session['user'].get('name', 'Utilisateur')

    # 2. INITIALISATION PAR DÉFAUT (Indispensable pour éviter l'erreur "no attribute")
    # On pré-remplit avec des 0 pour que le HTML ait toujours des données à lire
    stats_data = {
        'ca_total': 0,
        'taxes': 0,
        'total_salaires': 0,
        'entreprise': user_ent,
        'nom_user': user_name
    }
    ventes_list = []

    try:
        # 3. RÉCUPÉRATION SUPABASE
        # On essaie de récupérer les montants pour l'entreprise de l'utilisateur
        res = supabase.table("ventes").select("montant_net").eq("entreprise", user_ent).execute()
        
        if res.data:
            # Calcul du CA (on force la conversion en float pour éviter les bugs de type)
            total_ca = sum(float(v.get('montant_net', 0)) for v in res.data)
            
            # Mise à jour des stats avec les vrais chiffres
            stats_data['ca_total'] = total_ca
            stats_data['taxes'] = round(total_ca * 0.35, 2)
            # stats_data['total_salaires'] = ... (à ajouter si tu as une table salaires)

        # 4. RÉCUPÉRATION DES 5 DERNIÈRES VENTES POUR LE TABLEAU
        res_ventes = supabase.table("ventes").select("*").eq("entreprise", user_ent).order("id", desc=True).limit(5).execute()
        ventes_list = res_ventes.data if res_ventes.data else []

    except Exception as e:
        # Si ça plante ici, on print l'erreur dans les logs Vercel pour debug
        print(f"ERREUR CRITIQUE DASHBOARD : {e}")
        # Mais on ne crash pas ! stats_data contient déjà ses valeurs par défaut (0)

    # 5. ENVOI AU TEMPLATE (Note : on utilise bien 'stats=stats_data')
    return render_template('dashboard.html', stats=stats_data, ventes=ventes_list)

@app.route('/types-ventes')
def types_ventes_page():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    try:
        # Récupère le catalogue filtré par entreprise
        res = supabase.table("catalogue").select("*").eq("entreprise", user_ent).order("nom").execute()
        return render_template('types-ventes.html', catalogue=res.data)
    except Exception as e:
        return f"Erreur catalogue : {e}", 500

@app.route('/add_to_catalog', methods=['POST'])
def add_to_catalog():
    if 'user' not in session: return redirect(url_for('login'))
    nom = request.form.get('item_name')
    prix = request.form.get('item_price')
    stock = request.form.get('item_stock')
    user_ent = session['user'].get('entreprise')

    if nom and prix:
        try:
            supabase.table("catalogue").insert({
                "nom": nom, 
                "prix": float(prix),
                "stock": int(stock or 0),
                "entreprise": user_ent
            }).execute()
        except Exception as e:
            return f"Erreur ajout catalogue : {e}", 500
    return redirect(url_for('types_ventes_page'))

@app.route('/update_stock/<name>', methods=['POST'])
def update_stock(name):
    if 'user' not in session: return redirect(url_for('login'))
    nouveau_stock = request.form.get('nouveau_stock')
    try:
        valeur_stock = int(nouveau_stock) if nouveau_stock else 0
        # On filtre par "nom" au lieu de "id"
        supabase.table("catalogue").update({"stock": valeur_stock}).eq("nom", name).execute()
        return redirect(url_for('types_ventes_page'))
    except Exception as e:
        return f"Erreur stock : {e}", 500

@app.route('/catalogue/delete/<int:id>')
def delete_item_catalogue(id): # <--- C'est ce nom qui compte
    # ... logique ...
    if 'user' not in session: return redirect(url_for('login'))
    try:
        # On filtre par "nom" au lieu de "id"
        supabase.table("catalogue").delete().eq("nom", name).execute()
        return redirect(url_for('types_ventes_page'))
    except Exception as e:
        return f"Erreur suppression : {e}", 500

@app.route('/ventes')
def ventes_page():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    try:
        res_ventes = supabase.table("ventes").select("*").eq("entreprise", user_ent).order("id", desc=True).execute()
        res_cat = supabase.table("catalogue").select("*").eq("entreprise", user_ent).order("nom").execute()
        return render_template('ventes.html', 
                               ventes=res_ventes.data or [], 
                               catalogue=res_cat.data or [],
                               user=session['user'])
    except Exception as e:
        return f"Erreur ventes : {e}", 500

@app.route('/add_vente', methods=['POST'])
def add_vente():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    article = request.form.get('article')
    quantite = int(request.form.get('quantite') or 1)
    montant = float(request.form.get('montant') or 0)
    try:
        supabase.table("ventes").insert({
            "vendeur": session['user']['name'],
            "entreprise": user_ent,
            "article": article,
            "quantite": quantite,
            "montant_net": montant,
            "date": time.strftime("%d/%m %H:%M")
        }).execute()
        return redirect(url_for('ventes_page'))
    except Exception as e:
        return f"Erreur ajout vente : {e}", 500

@app.route('/delete_vente/<vente_id>')
def delete_vente(vente_id):
    if 'user' not in session: return redirect(url_for('login'))
    try:
        supabase.table("ventes").delete().eq("id", vente_id).execute()
    except Exception as e:
        print(f"Erreur suppression vente : {e}")
    return redirect(url_for('ventes_page'))

# --- SALAIRES & CLÔTURE ---

@app.route('/salaires')
def salaires_page():
    if 'user' not in session: return redirect(url_for('login'))
    ent = session['user'].get('entreprise')
    try:
        users = supabase.table("utilisateurs").select("*").eq("entreprise", ent).execute()
        ventes = supabase.table("ventes").select("*").eq("entreprise", ent).execute()
        grille = {"Recrue": 0.5, "Employé": 0.55, "Manager": 0.6, "Co patron": 0.63, "Patron": 0.65}
        liste_salaires = []
        for u in users.data:
            ca_emp = sum(v['montant_net'] for v in ventes.data if v['vendeur'] == u['name'])
            taux = grille.get(u['role'], 0.5)
            liste_salaires.append({
                "nom": u['name'], "grade": u['role'], "pourcentage": int(taux*100),
                "chiffre_affaire": ca_emp, "salaire_net": ca_emp * taux
            })
        return render_template('salaires.html', salaires=liste_salaires)
    except Exception as e:
        return f"Erreur salaires : {e}", 500

@app.route('/executer_cloture', methods=['POST'])
def executer_cloture():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    try:
        res = supabase.table("ventes").select("montant_net").eq("entreprise", user_ent).execute()
        ca_total = sum(float(v['montant_net']) for v in res.data) if res.data else 0
        taxes = round(ca_total * 0.35, 2)
        supabase.table("clotures").insert({
            "semaine_nom": "Clôture Semaine " + datetime.now().strftime("%U"),
            "ca_total": ca_total,
            "taxes_totales": taxes,
            "entreprise": user_ent
        }).execute()
        supabase.table("ventes").delete().eq("entreprise", user_ent).execute()
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Erreur clôture : {str(e)}", 500

# --- ROUTES SUPPLÉMENTAIRES ---

@app.route('/clotures')
def clotures_page():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    try:
        archives = supabase.table("clotures").select("*").eq("entreprise", user_ent).order("id", desc=True).execute()
        res_ventes = supabase.table("ventes").select("montant_net").eq("entreprise", user_ent).execute()
        ca_total = sum(float(v['montant_net']) for v in res_ventes.data)
        stats = {"ca": ca_total, "taxes": round(ca_total * 0.35, 2)}
        return render_template('clotures.html', archives=archives.data, stats=stats)
    except Exception as e:
        return f"Erreur archives : {e}", 500

@app.route('/irs')
def irs_page():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    try:
        res_ventes = supabase.table("ventes").select("montant_net").eq("entreprise", user_ent).execute()
        ca_total = sum(float(v['montant_net']) for v in res_ventes.data)
        stats = {"taxes": round(ca_total * 0.35, 2)}
        return render_template('irs.html', stats=stats)
    except Exception as e:
        return f"Erreur IRS : {e}", 500

@app.route('/utilisateurs')
def utilisateurs():
    if 'user' not in session: return redirect(url_for('login'))
    
    current_user = session['user']
    user_role = current_user.get('role')
    user_entreprise = current_user.get('entreprise')
    
    try:
        # 1. On récupère les utilisateurs
        query = supabase.table("utilisateurs").select("*")
        
        # Si ce n'est pas l'ADMIN (MASTER), on filtre par son entreprise uniquement
        if user_role != "MASTER":
            query = query.eq("entreprise", user_entreprise)
        
        response = query.execute()
        users_list = response.data if response.data else []
        
        # 2. On masque l'ADMIN (MASTER) de la liste pour tout le monde
        users_list = [u for u in users_list if u.get('role') != "MASTER"]
        
        # 3. Tri par grade
        ordre_grades = {"Patron": 1, "Co patron": 2, "Manager": 3, "Employé": 4}
        users_list.sort(key=lambda x: ordre_grades.get(x.get('role'), 99))
        
        # 4. Gestion de la liste des entreprises pour le menu déroulant
        # Seul l'admin voit tout. Le Patron/Co-Patron ne voit que la sienne.
        if user_role == "MASTER":
            liste_affichage_entreprises = ENTREPRISES_LISTE
        else:
            liste_affichage_entreprises = [user_entreprise]

        return render_template('utilisateurs.html', 
                               all_users=users_list, 
                               entreprises=liste_affichage_entreprises,
                               current_user_role=user_role) # On envoie le rôle pour le HTML
                               
    except Exception as e:
        print(f"Erreur : {e}")
        return f"Erreur serveur", 500
@app.route('/admin/select_entreprise', methods=['POST'])
def admin_select_entreprise():
    if 'user' not in session or session['user'].get('role') != 'MASTER':
        return redirect(url_for('login'))
    entreprise_choisie = request.form.get('entreprise_choisie')
    if entreprise_choisie:
        session['user']['entreprise'] = entreprise_choisie
        session.modified = True 
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
