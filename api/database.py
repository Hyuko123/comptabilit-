import json
import os

# Chemin absolu pour éviter les erreurs de dossier sur Vercel
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def charger_json(nom_fichier, defaut):
    chemin = os.path.join(DATA_DIR, nom_fichier)
    # Si le fichier n'existe pas, on renvoie la valeur par défaut au lieu de crash
    if not os.path.exists(chemin):
        return defaut
    try:
        with open(chemin, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return defaut

def charger_users(): return charger_json('users.json', {})
def charger_ventes(): return charger_json('ventes.json', [])
def charger_config_entreprises(): return charger_json('config_entreprises.json', {})

# Pour la sauvegarde (ne fonctionnera que temporairement sur Vercel)
def sauvegarder_json(nom_fichier, donnee):
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
        chemin = os.path.join(DATA_DIR, nom_fichier)
        with open(chemin, 'w', encoding='utf-8') as f:
            json.dump(donnee, f, indent=4, ensure_ascii=False)
    except:
        pass

def sauvegarder_users(u): sauvegarder_json('users.json', u)
