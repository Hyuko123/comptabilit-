from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'shinoza_ultraze_v2_key'

# --- LOGIQUE DE CONNEXION ---
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u = request.form.get('username')
    p = request.form.get('password')
    
    # Ton accès admin secret (Invisible dans le HTML)
    if u == "admin" and p == "admin123":
        session['user'] = {'name': 'Shinoza', 'role': 'Patron Global', 'entreprise': 'Ultraze Corp'}
        return redirect(url_for('dashboard'))
    
    # Simuler une connexion entreprise pour le test (Ex: Rex Diner)
    if u == "rex" and p == "rex123":
        session['user'] = {'name': 'Amare', 'role': 'Patron', 'entreprise': 'Rex Diner + LTD'}
        return redirect(url_for('dashboard'))

    return redirect(url_for('login'))

# --- ROUTES DASHBOARD & CATÉGORIES ---
@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    # Les stats sont calculées ici (Simulation selon tes images)
    stats = {'ca': 4650, 'salaires': 2558, 'taxes': 1628, 'benefice': 465}
    return render_template('dashboard.html', user=session['user'], stats=stats)

@app.route('/ventes')
def ventes():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('ventes.html', user=session['user'])

@app.route('/salaires')
def salaires():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('salaires.html', user=session['user'])

@app.route('/utilisateurs')
def utilisateurs():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('utilisateurs.html', user=session['user'])

@app.route('/stocks')
def stocks():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('stocks.html', user=session['user'])

@app.route('/clotures')
def clotures():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('clotures.html', user=session['user'])

@app.route('/irs')
def irs():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('irs.html', user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
