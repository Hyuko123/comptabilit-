import json
import os

# On définit le dossier DATA par rapport à la racine du projet Vercel
# Vercel place le code dans /var/task/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def charger_json(nom_fichier, defaut):
    chemin = os.path.join(DATA_DIR, nom_fichier)
    
    # LOG de debug pour voir où il cherche (visible dans les logs Vercel)
    print(f"Tentative de lecture : {chemin}")
    
    if not os.path.exists(chemin):
        print(f"Fichier MANQUANT : {chemin}")
        return defaut
    try:
        with open(chemin, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lecture JSON : {e}")
        return defaut

def sauvegarder_json(nom_fichier, donnee):
    # ATTENTION : Vercel n'autorise pas l'écriture permanente
    # Cette fonction marchera sur ton PC, mais pas sur Vercel
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
        chemin = os.path.join(DATA_DIR, nom_fichier)
        with open(chemin, 'w', encoding='utf-8') as f:
            json.dump(donnee, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"ERREUR ECRITURE (Normal sur Vercel) : {e}")

def charger_ventes(): return charger_json('ventes.json', [])
def sauvegarder_ventes(v): sauvegarder_json('ventes.json', v)
def charger_users(): return charger_json('users.json', {})
def sauvegarder_users(u): sauvegarder_json('users.json', u)
def charger_config_entreprises(): return charger_json('config_entreprises.json', {})
