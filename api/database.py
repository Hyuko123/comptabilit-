# api/database.py
import json
import os
from .config import USERS_DEFAULT

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
VENTES_FILE = os.path.join(BASE_DIR, 'data', 'ventes.json')
USERS_FILE = os.path.join(BASE_DIR, 'data', 'users.json')

def charger_ventes():
    if not os.path.exists(VENTES_FILE): return []
    with open(VENTES_FILE, 'r') as f: return json.load(f)

def sauvegarder_ventes(ventes):
    os.makedirs(os.path.dirname(VENTES_FILE), exist_ok=True)
    with open(VENTES_FILE, 'w') as f: json.dump(ventes, f, indent=4)

def charger_users():
    if not os.path.exists(USERS_FILE): return USERS_DEFAULT
    with open(USERS_FILE, 'r') as f: return json.load(f)

def sauvegarder_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f: json.dump(users, f, indent=4)
