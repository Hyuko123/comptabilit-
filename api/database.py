import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Chemins des fichiers
VENTES_FILE = os.path.join(DATA_DIR, 'ventes.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
ENTREPRISES_FILE = os.path.join(DATA_DIR, 'config_entreprises.json')

def charger_json(chemin, par_defaut):
    if not os.path.exists(chemin):
        return par_defaut
    with open(chemin, 'r', encoding='utf-8') as f:
        return json.load(f)

def sauvegarder_json(chemin, donnee):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(chemin, 'w', encoding='utf-8') as f:
        json.dump(donnee, f, indent=4, ensure_ascii=False)

# Fonctions spécifiques
def charger_ventes(): return charger_json(VENTES_FILE, [])
def sauvegarder_ventes(v): sauvegarder_json(VENTES_FILE, v)

def charger_users(): return charger_json(USERS_FILE, {})
def sauvegarder_users(u): sauvegarder_json(USERS_FILE, u)

def charger_config_entreprises(): return charger_json(ENTREPRISES_FILE, {})
def sauvegarder_config_entreprises(e): sauvegarder_json(ENTREPRISES_FILE, e)
