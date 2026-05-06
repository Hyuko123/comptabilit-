from flask import Flask, render_template, request, redirect, url_for, session
import time
from supabase import create_client, Client

# --- CONFIGURATION ---
SUPABASE_URL = "https://yiqpncfhfbltaalhgenp.supabase.co"
SUPABASE_KEY = "sb_publishable_GR_DdAtHA7_DB55cLywtrw_0TlybFWx" # Ta clé publishable

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

# --- ROUTES AUTH ---

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u = request.form.get('username')
    p = request.form.get('password')
    
    # On vérifie dans la table "utilisateurs" de Supabase
    res = supabase.table("utilisateurs").select("*").eq("username", u).execute()
    
    if res.data and res.data[0]['password'] == p:
        session['user'] = res.data[0]
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# --- ROUTES PRINCIPALES ---

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    
    # Récupérer les ventes de l'entreprise sur Supabase
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

@app.route('/utilisateurs')
def utilisateurs():
    if 'user' not in session: return redirect(url_for('login'))
    ent = session['user'].get('entreprise')
    
    # On récupère les employés de l'entreprise sur Supabase
    res = supabase.table("utilisateurs").select("*").eq("entreprise", ent).execute()
    return render_template('utilisateurs.html', all_users_list=res.data)

@app.route('/ventes')
def ventes_page():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    
    # Récupérer ventes + catalogue sur Supabase
    ventes = supabase.table("ventes").select("*").eq("entreprise", user_ent).order("id", desc=True).execute()
    cat = supabase.table("catalogue").select("*").order("nom").execute()
    
    return render_template('ventes.html', ventes=ventes.data, catalogue=cat.data, user=session['user'])

# --- ACTIONS (POST) ---

@app.route('/add_vente', methods=['POST'])
def add_vente():
    if 'user' not in session: return redirect(url_for('login'))
    
    article = request.form.get('article')
    quantite = int(request.form.get('quantite') or 1)
    montant = float(request.form.get('montant') or 0)
    
    supabase.table("ventes").insert({
        "vendeur": session['user']['name'],
        "entreprise": session['user']['entreprise'],
        "article": article,
        "quantite": quantite,
        "montant_net": montant,
        "date": time.strftime("%d/%m %H:%M")
    }).execute()
    
    return redirect(url_for('ventes_page'))

@app.route('/add_to_catalog', methods=['POST'])
def add_to_catalog():
    nom = request.form.get('item_name')
    prix = request.form.get('item_price')
    stock = request.form.get('item_stock')
    
    if nom and prix:
        supabase.table("catalogue").insert({
            "nom": nom, 
            "prix": float(prix),
            "stock": int(stock or 0)
        }).execute()
    return redirect('/types-ventes')

@app.route('/types-ventes')
def types_ventes_page():
    if 'user' not in session: return redirect(url_for('login'))
    res = supabase.table("catalogue").select("*").order("nom").execute()
    return render_template('type-ventes.html', catalogue=res.data)

@app.route('/salaires')
def salaires_page():
    if 'user' not in session: return redirect(url_for('login'))
    ent = session['user'].get('entreprise')
    
    # Tout récupérer sur Supabase
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
