from flask import Flask, render_template, request, redirect, url_for, session
import time
from supabase import create_client, Client
from datetime import datetime

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
        # On ne récupère QUE les ventes de CETTE entreprise
        res_ventes = supabase.table("ventes").select("*").eq("entreprise", user_ent).order("id", desc=True).execute()
        
        # CRUCIAL : On ne récupère QUE le catalogue de CETTE entreprise
        res_cat = supabase.table("catalogue").select("*").eq("entreprise", user_ent).order("nom").execute()
        
        return render_template('ventes.html', 
                               ventes=res_ventes.data or [], 
                               catalogue=res_cat.data or [],
                               user=session['user'])
    except Exception as e:
        return f"Erreur de connexion : {e}", 500

@app.route('/add_vente', methods=['POST'])
def add_vente():
    if 'user' not in session: return redirect(url_for('login'))
    
    user_ent = session['user'].get('entreprise') # On récupère l'entreprise en session
    article = request.form.get('article')
    quantite = int(request.form.get('quantite') or 1)
    montant = float(request.form.get('montant') or 0)
    
    try:
        supabase.table("ventes").insert({
            "vendeur": session['user']['name'],
            "entreprise": user_ent, # Verrouille la vente à l'entreprise actuelle
            "article": article,
            "quantite": quantite,
            "montant_net": montant,
            "date": time.strftime("%d/%m %H:%M")
        }).execute()
        
        return redirect(url_for('ventes_page'))
    except Exception as e:
        return f"Erreur lors de l'ajout de la vente : {e}", 500

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
    user_ent = session['user'].get('entreprise')

    try:
        # Récupération des ventes actuelles
        res = supabase.table("ventes").select("montant_net").eq("entreprise", user_ent).execute()
        
        # Calcul sécurisé du total
        ca_total = sum(float(v['montant_net']) for v in res.data) if res.data else 0
        taxes = round(ca_total * 0.35, 2)

        # Insertion dans les archives
        supabase.table("clotures").insert({
            "semaine_nom": "Clôture Semaine " + datetime.now().strftime("%U"),
            "ca_total": ca_total,
            "taxes_totales": taxes,
            "entreprise": user_ent
        }).execute()

        # Suppression des ventes (Reset)
        supabase.table("ventes").delete().eq("entreprise", user_ent).execute()

        return redirect(url_for('dashboard'))
    except Exception as e:
        # Affiche l'erreur réelle au lieu d'une page blanche
        return f"Erreur lors de la clôture : {str(e)}", 500

@app.route('/clotures')
def clotures_page():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    
    try:
        # Récupère l'historique des clôtures pour l'entreprise
        archives = supabase.table("clotures").select("*").eq("entreprise", user_ent).order("date_cloture", desc=True).execute()
        
        # Récupère les stats actuelles (CA et Taxes) avant clôture
        res_ventes = supabase.table("ventes").select("montant_net").eq("entreprise", user_ent).execute()
        ca_total = sum(float(v['montant_net']) for v in res_ventes.data)
        
        stats = {
            "ca": ca_total,
            "taxes": round(ca_total * 0.35, 2)
        }
        
        return render_template('clotures.html', archives=archives.data, stats=stats)
    except Exception as e:
        return f"Erreur : {e}", 500

@app.route('/irs')
def irs_page():
    if 'user' not in session: return redirect(url_for('login'))
    user_ent = session['user'].get('entreprise')
    
    # Récupère le CA actuel pour calculer les taxes en temps réel
    res_ventes = supabase.table("ventes").select("montant_net").eq("entreprise", user_ent).execute()
    ca_total = sum(float(v['montant_net']) for v in res_ventes.data)
    
    stats = {
        "taxes": round(ca_total * 0.35, 2)
    }
    
    return render_template('irs.html', stats=stats)

@app.route('/admin/select_entreprise', methods=['POST'])
def admin_select_entreprise():
    # Sécurité : on vérifie que tu es bien MASTER
    if 'user' not in session or session['user'].get('role') != 'MASTER':
        return redirect(url_for('login'))

    entreprise_choisie = request.form.get('entreprise_choisie')
    
    if entreprise_choisie:
        # On remplace l'entreprise actuelle par celle choisie
        session['user']['entreprise'] = entreprise_choisie
        session.modified = True 
        print(f"Switch réussi vers : {entreprise_choisie}")
        
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
