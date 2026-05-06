# api/config.py

PRODUITS_PAR_ENTREPRISE = {
    "Burger Shot": {"Menu Burger": 75, "Frites": 20, "Soda": 15},
    "Unicorn": {"Entrée Club": 100, "Bouteille Champagne": 500, "Cocktail": 50},
    "LTD Little Seoul": {"Sachet de chips": 10, "Eau": 5, "Barre chocolatée": 8},
    "ADMINISTRATION": {"Service Admin": 0, "Licence": 1000}
}

# Utilisateurs par défaut si le fichier JSON est vide au premier lancement
USERS_DEFAULT = {
    "admin": {
        "password": "123", 
        "name": "Admin", 
        "role": "Patron", 
        "entreprise": "ADMINISTRATION",
        "taux": 100, "telephone": "555-ADMIN", "iban": "SA-ADMIN-01", "prime": 0, "avance": 0
    },
    "shinoza": {
        "password": "123", 
        "name": "Shinoza", 
        "role": "Co Patron", 
        "entreprise": "Burger Shot",
        "taux": 65, "telephone": "555-9874", "iban": "LS-BS-098", "prime": 150, "avance": 0
    }
}
