import json
import os

# Cette ligne est magique : elle trouve le dossier parent, peu importe où le code tourne
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def charger_json(nom_fichier, defaut):
    chemin = os.path.join(DATA_DIR, nom_fichier)
    if not os.path.exists(chemin):
        return defaut
    try:
        with open(chemin, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return defaut

def sauvegarder_json(nom_fichier, donnee):
    # Sur Vercel, l'écriture peut échouer, on ajoute un try/except
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
        chemin = os.path.join(DATA_DIR, nom_fichier)
        with open(chemin, 'w', encoding='utf-8') as f:
            json.dump(donnee, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur d'écriture : {e}")

def charger_ventes(): return charger_json('ventes.json', [])
def sauvegarder_ventes(v): sauvegarder_json('ventes.json', v)
def charger_users(): return charger_json('users.json', {})
def sauvegarder_users(u): sauvegarder_json('users.json', u)
def charger_config_entreprises(): return charger_json('config_entreprises.json', {})
