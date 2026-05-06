from flask import Flask, render_template

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # On simule des données pour éviter les erreurs de calcul au début
    stats = {
        "ca_net": 0,
        "taxes": 0,
        "benefice": 0
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/ventes')
def ventes():
    return render_template('ventes.html')

# Ajoute ces routes pour éviter les erreurs 404 au clic
@app.route('/salaires')
def salaires():
    return "Page Salaires en construction"

@app.route('/utilisateurs')
def utilisateurs():
    return "Page Utilisateurs en construction"

if __name__ == '__main__':
    app.run(debug=True)
