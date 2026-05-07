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
    
    try:
        # On cherche l'utilisateur par son username
        res = supabase.table("utilisateurs").select("*").eq("username", u).execute()
        
        # On vérifie si on a trouvé quelqu'un
        if res.data and len(res.data) > 0:
            user_data = res.data[0]
            # Vérification du mot de passe (en texte brut ici selon ta capture)
            if str(user_data.get('password')) == str(p):
                session['user'] = user_data
                return redirect(url_for('dashboard'))
        
        # Si ça échoue, on retourne au login
        return redirect(url_for('login'))
        
    except Exception as e:
        # Ceci évitera l'erreur 500 en affichant l'erreur au lieu de crash
        return f"Erreur de connexion à la base de données : {e}", 500

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
    if 'user' not in session: 
        return redirect(url_for('login'))
    
    user_ent = session['user'].get('entreprise')
    
    try:
        # On récupère les données
        res_ventes = supabase.table("ventes").select("*").eq("entreprise", user_ent).order("id", desc=True).execute()
        res_cat = supabase.table("catalogue").select("*").order("nom").execute()
        
        # On vérifie si Supabase a renvoyé une erreur de permission
        if hasattr(res_ventes, 'error') and res_ventes.error:
            return f"Erreur Supabase (Ventes): {res_ventes.error}", 500
            
        return render_template('ventes.html', 
                               ventes=res_ventes.data or [], 
                               catalogue=res_cat.data or [],
                               user=session['user'])
    except Exception as e:
        return f"Erreur de connexion : {e}", 500

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

@app.route('/delete_vente/<int:vente_id>')
def delete_vente(vente_id):
    if 'user' not in session: return redirect(url_for('login'))
    
    try:
        supabase.table("ventes").delete().eq("id", vente_id).execute()
    except Exception as e:
        print(f"Erreur suppression : {e}")

@app.route('/executer_cloture', methods=['POST'])
def executer_cloture():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user']['entreprise']

    # 1. Calculer les totaux actuels avant de supprimer
    res = supabase.table("ventes").select("montant_net").eq("entreprise", user_ent).execute()
    ca_total = sum(float(v['montant_net']) for v in res.data)
    taxes = ca_total * 0.35 # Ton taux de 35% sur le screen

    # 2. Archiver dans la table clotures
    supabase.table("clotures").insert({
        "semaine_nom": "Semaine " + datetime.now().strftime("%U"),
        "ca_total": ca_total,
        "taxes_totales": taxes,
        "entreprise": user_ent
    }).execute()

    # 3. REMISE À ZÉRO : On supprime les ventes de cette entreprise
    supabase.table("ventes").delete().eq("entreprise", user_ent).execute()

    return redirect(url_for('dashboard'))
        
    return redirect(url_for('ventes_page'))

if __name__ == '__main__':
    app.run(debug=True)
