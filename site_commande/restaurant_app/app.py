import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import json


# ---------- Flask ----------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "ChangeMoi123!")

# ---------- PostgreSQL ----------
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")  # docker-compose service name

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------- Models ----------
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    plats = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default='en préparation')

# ---------- Restaurateur ----------
USERNAME = os.getenv("RESTO_USER", "admin")
PASSWORD = os.getenv("RESTO_PASSWORD", "motdepasse")

# ---------- Routes Frontend ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user == USERNAME and pwd == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Identifiants invalides")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/client')
def client():
    table = request.args.get('table')
    if not table:
        return "Table non spécifiée", 400
    return render_template('client.html', table=table)

@app.route('/api/menu')
def get_menu():
    with open('menu.json') as f:
        menu = json.load(f)
    return jsonify(menu)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# ---------- API ----------
@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([
        {'id': o.id, 'table_number': o.table_number, 'plats': o.plats.split(','), 'status': o.status} 
        for o in orders
    ])

@app.route('/api/orders', methods=['POST'])
def add_order():
    data = request.json
    table = data.get('table')
    plats = data.get('plats', [])
    if table and plats:
        order = Order(table_number=table, plats=','.join(plats))
        db.session.add(order)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Données manquantes'}), 400

@app.route('/api/orders/<int:table>/ready', methods=['POST'])
def mark_ready(table):
    order = Order.query.filter_by(table_number=table).first()
    if order:
        order.status = 'PRÊT'
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Commande non trouvée'}), 404

@app.route('/api/orders/<int:table>/clear', methods=['POST'])
def clear_table(table):
    orders = Order.query.filter_by(table_number=table).all()
    for order in orders:
        db.session.delete(order)
    db.session.commit()
    return jsonify({'success': True})

# ---------- Run ----------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=5000, debug=True)