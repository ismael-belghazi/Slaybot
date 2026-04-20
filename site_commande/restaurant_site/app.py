import os
import json
import uuid
import threading
import websocket
from functools import wraps
from collections import defaultdict
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
import eventlet

eventlet.monkey_patch()

# ----------------- App & Config -----------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

socketio = SocketIO(app, cors_allowed_origins="*", manage_session=True)

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "restaurant")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ----------------- Models -----------------
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    plats = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default='EN_ATTENTE')
    token = db.Column(db.String, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    cancelled_at = db.Column(db.DateTime, nullable=True)

class TableToken(db.Model):
    __tablename__ = 'table_tokens'
    token = db.Column(db.String, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

# ----------------- Auth Config -----------------
USERNAME = os.getenv("RESTO_USER", "admin")
PASSWORD = os.getenv("RESTO_PASSWORD", "admin")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ----------------- Helpers -----------------
table_clients = defaultdict(set)  # table_number -> set(socket IDs)
socket_to_table = {}  # sid -> table number

def get_table_summary(table_number):
    orders = Order.query.filter_by(table_number=table_number, paid=False).all()
    summary = {}
    total = 0

    with open('menu.json') as f:
        menu = json.load(f)

    all_items = {i['name']: i['price'] for cat in ['entrees','plats','desserts','boissons'] for i in menu.get(cat, [])}

    for order in orders:
        if not order.plats:
            continue
        for p in order.plats.split(','):
            name, qty = p.split(':')
            qty = int(qty)
            summary[name] = summary.get(name, 0) + qty
            total += all_items.get(name, 0) * qty

    return {'summary': summary, 'total': round(total,2)}


def serialize_order(order):
    plats = []
    if order.plats:
        for p in order.plats.split(','):
            if ':' in p:
                name, qty = p.split(':', 1)
                for _ in range(int(qty)):
                    plats.append(name)
    return {
        'id': order.id,
        'table': order.table_number,
        'plats': plats,
        'status': (order.status or 'EN_ATTENTE').upper()
    }


def get_dashboard_orders():
    orders = Order.query.filter_by(paid=False).all()
    return [serialize_order(order) for order in orders]


def validate_token(table_number, token):
    if not token:
        return False
    token_obj = TableToken.query.get(token)
    return bool(token_obj and token_obj.active and token_obj.table_number == table_number)


def activate_token(table_number, token):
    token_obj = TableToken.query.get(token)
    if token_obj:
        if token_obj.table_number != table_number or not token_obj.active:
            return None
        return token_obj

    token_obj = TableToken(token=token, table_number=table_number, active=True)
    db.session.add(token_obj)
    db.session.commit()
    return token_obj


def invalidate_token(token):
    token_obj = TableToken.query.get(token)
    if token_obj:
        token_obj.active = False
        db.session.commit()
    return token_obj


def invalidate_table_tokens(table_number):
    tokens = TableToken.query.filter_by(table_number=table_number, active=True).all()
    for token in tokens:
        token.active = False
    db.session.commit()
    return tokens


class HotspotBridge:
    ws = None
    connected = False
    url = os.getenv('HOTSPOT_WS_URL', 'ws://10.42.0.1:8765')

    @classmethod
    def connect(cls):
        def on_message(ws, message):
            print(f"[HOTSPOT] reçu : {message}")

        def on_open(ws):
            cls.connected = True
            print("[HOTSPOT] Connecté au serveur cerveau")

        def on_close(ws, close_status_code, close_msg):
            cls.connected = False
            print("[HOTSPOT] Déconnecté du serveur cerveau")

        def on_error(ws, error):
            print(f"[HOTSPOT] Erreur : {error}")

        cls.ws = websocket.WebSocketApp(
            cls.url,
            on_message=on_message,
            on_open=on_open,
            on_close=on_close,
            on_error=on_error
        )
        threading.Thread(target=cls.ws.run_forever, daemon=True).start()

    @classmethod
    def send(cls, message):
        if cls.ws and cls.connected:
            try:
                cls.ws.send(message)
                print(f"[HOTSPOT] envoyé : {message}")
            except Exception as ex:
                print(f"[HOTSPOT] impossible d'envoyer : {ex}")
        else:
            print(f"[HOTSPOT] pas connecté, message ignoré : {message}")

    @classmethod
    def send_order(cls, table_number):
        cls.send(f"order/table/{table_number}")

    @classmethod
    def send_cancel(cls, table_number):
        cls.send(f"cancel/table/{table_number}")

    @classmethod
    def send_payment(cls, table_number):
        cls.send(f"paid/table/{table_number}")


def update_order_item(table_number, token, item_name, delta, replace=False):
    """
    Met à jour une commande :
    - delta : quantité à ajouter
    - replace=True : remplace la quantité existante par delta
    """
    order = Order.query.filter_by(table_number=table_number, token=token, paid=False).first()
    plats_dict = {}
    if order and order.plats:
        for p in order.plats.split(','):
            name, qty = p.split(':')
            plats_dict[name] = int(qty)

    if replace:
        plats_dict[item_name] = delta
    else:
        plats_dict[item_name] = plats_dict.get(item_name, 0) + delta

    plats_dict = {k: v for k,v in plats_dict.items() if v > 0}

    if order:
        order.plats = ','.join(f"{k}:{v}" for k,v in plats_dict.items())
    else:
        order = Order(
            table_number=table_number,
            plats=','.join(f"{k}:{v}" for k,v in plats_dict.items()),
            token=token
        )
        db.session.add(order)
    db.session.commit()

# ----------------- Routes -----------------
@app.route('/')
def home():
    return redirect(url_for('dashboard') if session.get('logged_in') else url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user == USERNAME and pwd == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Identifiants invalides")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/client')
def client():
    table = request.args.get('table')
    if not table:
        return "Table non spécifiée", 400
    table = int(table)

    token = request.args.get('token')
    if not token:
        order = Order.query.filter_by(table_number=table, paid=False).first()
        token = order.token if order else str(uuid.uuid4())

    token_obj = activate_token(table, token)
    if not token_obj:
        return "Le token est invalide ou expiré. Scannez un nouveau QR code.", 403

    session['table_token'] = token
    return render_template('client.html', table=table, token=token)

@app.route('/api/menu')
def get_menu():
    with open('menu.json') as f:
        menu = json.load(f)
    return jsonify(menu)

# ----------------- SocketIO -----------------
@socketio.on('connect')
def handle_connect():
    sid = request.sid
    if session.get('logged_in'):
        join_room('dashboard')
        emit('update_orders', get_dashboard_orders(), room=sid)
        return

    # Les clients de table rejoignent la salle via l'événement join_table
    return

@socketio.on('join_table')
def handle_join_table(data):
    sid = request.sid
    table_raw = data.get('table')
    token = data.get('token')
    if not table_raw or not token:
        print(f"[WARN] join_table missing data: {data}")
        emit('join_error', {'message': 'Table ou token manquant'})
        return

    table = int(table_raw)
    if not validate_token(table, token):
        print(f"[WARN] join_table invalid token: {token}")
        emit('join_error', {'message': 'Token invalide ou expiré'})
        return

    join_room(f"table_{table}")
    table_clients[table].add(sid)
    socket_to_table[sid] = table
    session['table_token'] = token

    print(f"[WS] table {table} joined with sid {sid}")
    emit('joined_table', {'table': table}, room=sid)
    emit('update_summary', get_table_summary(table), room=f"table_{table}")
    emit('update_clients_count', len(table_clients[table]), room=f"table_{table}")

@socketio.on('join_dashboard')
def handle_join_dashboard():
    sid = request.sid
    if not session.get('logged_in'):
        print(f"[WARN] join_dashboard rejected: non autorisé")
        emit('join_error', {'message': 'Non autorisé'})
        return

    join_room('dashboard')
    print(f"[WS] dashboard joined with sid {sid}")
    emit('update_orders', get_dashboard_orders(), room=sid)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    table = socket_to_table.pop(sid, None)
    if table is not None:
        clients = table_clients.get(table, set())
        if sid in clients:
            clients.remove(sid)
            socketio.emit('update_clients_count', len(clients), room=f"table_{table}")

@socketio.on('update_item')
def handle_update_item(data):
    table_raw = data.get('table')
    token = data.get('token')
    item_name = data.get('item')
    quantityDelta = int(data.get('quantityDelta', 0))

    if not table_raw or not token or not item_name:
        print(f"[WARN] update_item missing data: {data}")
        return

    table = int(table_raw)
    if not validate_token(table, token):
        print(f"[WARN] update_item invalid token: {token}")
        return

    update_order_item(table, token, item_name, quantityDelta)
    socketio.emit('update_summary', get_table_summary(table), room=f"table_{table}")

@socketio.on('request_summary')
def handle_request_summary(data):
    table_raw = data.get('table')
    token = data.get('token')
    if not table_raw or not token:
        return

    table = int(table_raw)
    if not validate_token(table, token):
        return

    emit('update_summary', get_table_summary(table), room=f"table_{table}")

# ----------------- SocketIO -----------------
@socketio.on('send_order')
def handle_send_order(data):
    table_raw = data.get('table')
    token = data.get('token')
    order_dict = data.get('order')

    if not table_raw or not token or not order_dict:
        print(f"[WARN] send_order missing data: {data}")
        return

    table = int(table_raw)
    if not validate_token(table, token):
        print(f"[WARN] send_order invalid token: {token}")
        return

    existing_orders = Order.query.filter_by(table_number=table, paid=False).all()
    if existing_orders:
        already_active = any(order.status in ['EN_ATTENTE', 'PRET'] for order in existing_orders)
        if already_active:
            print(f"[INFO] send_order ignored, table {table} already has an active order")
            socketio.emit('order_already_submitted', {'table': table}, room=f"table_{table}")
            socketio.emit('update_summary', get_table_summary(table), room=f"table_{table}")
            return

    # CRÉER une nouvelle commande avec exactement les quantités envoyées
    new_order = Order(
        table_number=table,
        token=token,
        plats=','.join(f"{k}:{v}" for k,v in order_dict.items()),
        status='EN_ATTENTE'
    )
    db.session.add(new_order)
    db.session.commit()

    print(f"[INFO] Nouvelle commande pour table {table}: {order_dict}")
    socketio.emit('update_summary', get_table_summary(table), room=f"table_{table}")
    socketio.emit('order_submitted', {'table': table}, room=f"table_{table}")
    socketio.emit('update_orders', get_dashboard_orders(), room='dashboard')
    
# ----------------- SocketIO -----------------
@socketio.on('confirm_order')
def handle_confirm_order(data):
    if not session.get('logged_in'):
        print(f"[WARN] confirm_order rejected: non autorisé")
        return

    table = int(data.get('table'))
    orders = Order.query.filter_by(table_number=table, paid=False).all()
    if not orders:
        print(f"[WARN] confirm_order no unpaid order for table {table}")
        return

    already_ready = all(order.status == 'PRET' for order in orders)
    if already_ready:
        print(f"[INFO] confirm_order ignored, table {table} already PRET")
        return

    for order in orders:
        order.status = 'PRET'
    db.session.commit()

    print(f"[INFO] Table {table} confirmed and sent to hotspot")
    HotspotBridge.send_order(table)
    socketio.emit('order_ready', {'table': table}, room=f"table_{table}")
    socketio.emit('update_orders', get_dashboard_orders(), room='dashboard')
    socketio.emit('update_summary', get_table_summary(table), room=f"table_{table}")

@socketio.on('cancel_order')
def handle_cancel_order(data):
    if not session.get('logged_in'):
        print(f"[WARN] cancel_order rejected: non autorisé")
        return

    table = int(data.get('table'))
    orders = Order.query.filter_by(table_number=table, paid=False).all()
    for order in orders:
        db.session.delete(order)
    db.session.commit()

    HotspotBridge.send_cancel(table)
    socketio.emit('update_orders', get_dashboard_orders(), room='dashboard')
    socketio.emit('update_summary', get_table_summary(table), room=f"table_{table}")
    socketio.emit('order_cleared', {'table': table}, room=f"table_{table}")

# Exemple côté serveur (SocketIO)
@socketio.on('complete_order')
def handle_complete_order(data):
    if not session.get('logged_in'):
        print(f"[WARN] complete_order rejected: non autorisé")
        return

    table = int(data.get('table'))
    token = data.get('token')
    orders = Order.query.filter_by(table_number=table, token=token).all()
    for order in orders:
        db.session.delete(order)
    db.session.commit()
    socketio.emit('order_completed', {'table': table, 'token': token}, room=f"table_{table}")

@socketio.on('pay_order')
def handle_pay(data):
    if not session.get('logged_in'):
        print(f"[WARN] pay_order rejected: non autorisé")
        return

    table = int(data.get('table'))

    orders = Order.query.filter_by(table_number=table, paid=False).all()
    for order in orders:
        db.session.delete(order)
    invalidate_table_tokens(table)
    db.session.commit()

    socketio.emit('update_summary', get_table_summary(table), room=f"table_{table}")
    socketio.emit('session_ended', {'table': table}, room=f"table_{table}")
    socketio.emit('order_cleared', {'table': table}, room=f"table_{table}")
    socketio.emit('update_orders', get_dashboard_orders(), room='dashboard')
    HotspotBridge.send_payment(table)

# ----------------- Run App -----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.start_background_task(HotspotBridge.connect)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)