import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def charger_json(nom_fichier, defaut):
    chemin = os.path.join(DATA_DIR, nom_fichier)
    if not os.path.exists(chemin):
        return defaut
    with open(chemin, 'r', encoding='utf-8') as f:
        return json.load(f)

def sauvegarder_json(nom_fichier, donnee):
    os.makedirs(DATA_DIR, exist_ok=True)
    chemin = os.path.join(DATA_DIR, nom_fichier)
    with open(chemin, 'w', encoding='utf-8') as f:
        json.dump(donnee, f, indent=4, ensure_ascii=False)

# Fonctions d'accès
def charger_ventes(): return charger_json('ventes.json', [])
def sauvegarder_ventes(v): sauvegarder_json('ventes.json', v)

def charger_users(): return charger_json('users.json', {})
def sauvegarder_users(u): sauvegarder_json('users.json', u)

def charger_config_entreprises(): return charger_json('config_entreprises.json', {})
def sauvegarder_config_entreprises(e): sauvegarder_json('config_entreprises.json', e)
