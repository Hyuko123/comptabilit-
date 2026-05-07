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
    # Ces noms doivent être IDENTIQUES aux 'name' du fichier HTML
    username = request.form.get('new_username') # Utilise 'new_username' ici
    name = request.form.get('new_name')
    password = request.form.get('new_password')
    role = request.form.get('new_role')
    entreprise = request.form.get('new_entreprise')
    
    # ... code d'insertion Supabase ...

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
            print(f"Erreur insertion utilisateur : {e}")
            return f"Erreur : {e}", 500
            
    return redirect(url_for('utilisateurs'))

# --- DASHBOARD ---

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    try:
        res = supabase.table("ventes").select("montant_net").eq("entreprise", user_ent).execute()
        ca = sum(v.get('montant_net', 0) for v in res.data)
        stats = {
            'ca': ca,
            'taxes': int(ca * 0.15),
            'benefice': int(ca * 0.85),
            'nom_user': session['user'].get('name'),
            'entreprise': user_ent
        }
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        return f"Erreur Dashboard : {e}", 500

# --- CATALOGUE & STOCK ---

@app.route('/types-ventes')
def types_ventes_page():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    try:
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

@app.route('/delete_catalogue/<id>')
def delete_catalogue(id):
    if 'user' not in session: return redirect(url_for('login'))
    try:
        # On force la conversion en entier au cas où
        supabase.table("catalogue").delete().eq("id", int(id)).execute()
    except Exception as e:
        # Si c'est déjà un texte, on essaie sans conversion
        supabase.table("catalogue").delete().eq("id", str(id)).execute()
    return redirect(url_for('types_ventes_page'))

@app.route('/update_stock/<id>', methods=['POST'])
def update_stock(id):
    if 'user' not in session: return redirect(url_for('login'))
    nouveau_stock = request.form.get('nouveau_stock')
    if nouveau_stock is not None:
        try:
            # On force l'ID en entier et le stock en entier
            supabase.table("catalogue").update({"stock": int(nouveau_stock)}).eq("id", int(id)).execute()
        except:
            # Si l'ID est un texte (UUID)
            supabase.table("catalogue").update({"stock": int(nouveau_stock)}).eq("id", str(id)).execute()
    return redirect(url_for('types_ventes_page'))

# --- VENTES ---

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
    
    # 1. On récupère les entreprises pour le menu déroulant
    # (Soit via un JSON, soit via Supabase)
    entreprises = ["Restaurant Vinewood", "Unicorn", "Pop Chiken"] 

    # 2. On récupère la liste des employés DEPUIS Supabase
    try:
        response = supabase.table("utilisateurs").select("*").execute()
        all_users = response.data
    except Exception as e:
        print(f"Erreur de lecture : {e}")
        all_users = []

    return render_template('utilisateurs.html', 
                           all_users=all_users, 
                           entreprises=entreprises)

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
