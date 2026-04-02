import threading
import websocket
import json
import os
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp

CONFIG_FILE = "config.json"

# =============================================================================
# GESTION DES COMMUNICATIONS (WebSocket)
# =============================================================================
class RobotAPI:
    ws = None
    online = False
    callback = None
    robot_ip = "10.42.0.1"
    port = 8765

    @staticmethod
    def connect():
        if RobotAPI.ws:
            RobotAPI.ws.close()

        def on_msg(ws, message):
            msg = message.strip().lower()
            # 1. Réception d'une commande de table (ex: "order/table/1")
            if "order/table/" in msg:
                table_id = msg.split("/")[-1]
                if MainScreen.instance:
                    Clock.schedule_once(lambda dt: MainScreen.instance.notify_new_order(table_id))
            
            # 2. Le robot signale qu'il est revenu à sa base
            elif "arrived/bar" in msg:
                if MainScreen.instance:
                    Clock.schedule_once(lambda dt: MainScreen.instance.on_mission_complete())

        def on_open(ws): 
            RobotAPI.online = True
            if RobotAPI.callback:
                Clock.schedule_once(lambda dt: RobotAPI.callback("Connecté"))

        def on_close(ws, x, y): 
            RobotAPI.online = False
            if RobotAPI.callback:
                Clock.schedule_once(lambda dt: RobotAPI.callback("Déconnecté"))

        uri = f"ws://{RobotAPI.robot_ip}:{RobotAPI.port}"
        RobotAPI.ws = websocket.WebSocketApp(uri, on_message=on_msg, on_open=on_open, on_close=on_close)
        threading.Thread(target=RobotAPI.ws.run_forever, daemon=True).start()

    @staticmethod
    def send(cmd):
        if RobotAPI.ws and RobotAPI.online:
            try:
                RobotAPI.ws.send(cmd)
            except:
                pass

# =============================================================================
# LOGIQUE MÉTIER ET INTERFACE PRINCIPALE
# =============================================================================
class MainScreen(Screen):
    instance = None
    status = StringProperty("Connexion...")
    queue = ListProperty([])              # File d'attente du Robot
    orders_to_prepare = ListProperty([])  # File d'attente Cuisine (Validation)
    is_busy = False 

    def __init__(self, **kw):
        super().__init__(**kw)
        MainScreen.instance = self

    def on_enter(self):
        RobotAPI.callback = self.set_status
        Clock.schedule_interval(self.check_queue, 1)

    def set_status(self, text): 
        self.status = text

    # --- Gestion de la Cuisine (Validation Humaine) ---
    def notify_new_order(self, table_id):
        """ Reçu via WebSocket : On demande à l'utilisateur de préparer. """
        task = f"Table {table_id}"
        if task not in self.orders_to_prepare and task not in self.queue:
            self.orders_to_prepare.append(task)
            self.update_orders_ui()

    def validate_order(self, task_name):
        """ L'utilisateur valide que la commande est prête à partir. """
        if task_name in self.orders_to_prepare:
            self.orders_to_prepare.remove(task_name)
            self.update_orders_ui()
            # On envoie maintenant dans la file du robot
            table_id = task_name.split()[-1]
            self.add_to_queue(table_id)

    def update_orders_ui(self):
        container = self.ids.orders_list
        container.clear_widgets()
        for item in self.orders_to_prepare:
            line = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            lbl = Label(text=f"[b]{item}[/b]\n[size=12sp]À PRÉPARER[/size]", markup=True, halign='left')
            btn = Button(text="PRÊT", size_hint_x=None, width=dp(80), 
                         background_normal='', background_color=(0, 0.6, 0.3, 1))
            btn.bind(on_release=lambda x, it=item: self.validate_order(it))
            line.add_widget(lbl)
            line.add_widget(btn)
            container.add_widget(line)

    # --- Gestion du Robot (Livraison) ---
    def add_to_queue(self, table_id):
        task = f"Table {table_id}"
        if task not in self.queue:
            self.queue.append(task)
            self.update_queue_ui()

    def remove_from_queue(self, task_name):
        if task_name in self.queue:
            if self.queue.index(task_name) == 0 and self.is_busy:
                self.is_busy = False
            self.queue.remove(task_name)
            self.update_queue_ui()

    def update_queue_ui(self):
        container = self.ids.queue_list
        container.clear_widgets()
        for item in self.queue:
            line = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
            lbl = Label(text=item, halign='left')
            btn = Button(text="X", size_hint_x=None, width=dp(45), 
                         background_normal='', background_color=(0.8, 0.2, 0.2, 1))
            btn.bind(on_release=lambda x, it=item: self.remove_from_queue(it))
            line.add_widget(lbl)
            line.add_widget(btn)
            container.add_widget(line)

    def on_mission_complete(self):
        if self.queue:
            self.queue.pop(0)
            self.update_queue_ui()
        self.is_busy = False
        self.status = "Prêt"

    def check_queue(self, dt):
        if self.queue and not self.is_busy and RobotAPI.online:
            next_table = self.queue[0].split()[-1]
            RobotAPI.send(f"go/{next_table}")
            self.is_busy = True
            self.status = f"En route : Table {next_table}"

    def reconnect(self):
        RobotAPI.connect()

class SettingsScreen(Screen):
    def save_config(self, new_ip):
        RobotAPI.robot_ip = new_ip
        with open(CONFIG_FILE, "w") as f:
            json.dump({"ip": new_ip}, f)
        RobotAPI.connect()
        self.manager.current = "main"

class RobotApp(App):
    def build(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                try:
                    data = json.load(f)
                    RobotAPI.robot_ip = data.get("ip", "127.0.0.1")
                except: pass
        RobotAPI.connect()
        return Builder.load_string(KV)

# --- DESIGN KV ---
KV = '''
<StyledButton@Button>:
    background_normal: ''
    background_down: ''
    font_size: '16sp'
    bold: True
    canvas.before:
        Color:
            rgba: (self.background_color[0]*0.6, self.background_color[1]*0.6, self.background_color[2]*0.6, 1) if self.state == 'down' else self.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]

ScreenManager:
    MainScreen:
    SettingsScreen:

<MainScreen>:
    name: "main"
    BoxLayout:
        orientation: "horizontal"
        canvas.before:
            Color:
                rgb: 0.08, 0.08, 0.12
            Rectangle:
                pos: self.pos
                size: self.size

        # PANNEAU DE COMMANDE (GAUCHE)
        BoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(15)

            Label:
                text: root.status
                font_size: "22sp"
                bold: True
                color: (0, 0.9, 0.5, 1) if "Connecté" in self.text or "route" in self.text else (0.9, 0.2, 0.2, 1)
                size_hint_y: None
                height: dp(50)

            GridLayout:
                cols: 2
                spacing: dp(15)
                StyledButton:
                    text: "TABLE 1"
                    background_color: 0.2, 0.4, 0.9, 1
                    on_press: root.notify_new_order("1")
                StyledButton:
                    text: "TABLE 2"
                    background_color: 0.9, 0.7, 0.1, 1
                    on_press: root.notify_new_order("2")
                StyledButton:
                    text: "TABLE 3"
                    background_color: 0.8, 0.1, 0.1, 1
                    on_press: root.notify_new_order("3")
                StyledButton:
                    text: "TABLE 4"
                    background_color: 0.1, 0.7, 0.2, 1
                    on_press: root.notify_new_order("4")

            Widget:
                size_hint_y: 1 

            BoxLayout:
                size_hint_y: None
                height: dp(55)
                spacing: dp(10)
                StyledButton:
                    text: "RECO"
                    background_color: 0.1, 0.5, 0.3, 1
                    on_press: root.reconnect()
                StyledButton:
                    text: "PARAMS"
                    background_color: 0.3, 0.3, 0.3, 1
                    on_press: app.root.current = "settings"

        # PANNEAU DE SUIVI (DROITE)
        BoxLayout:
            orientation: "vertical"
            size_hint_x: 0.55
            padding: dp(15)
            spacing: dp(10)
            canvas.before:
                Color:
                    rgb: 0.14, 0.14, 0.18
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(20), 0, 0, dp(20)]

            Label:
                text: "--- CUISINE ---"
                bold: True
                color: 1, 0.7, 0, 1
                size_hint_y: None
                height: dp(30)

            ScrollView:
                size_hint_y: 0.5
                BoxLayout:
                    id: orders_list
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(8)

            Widget:
                size_hint_y: None
                height: dp(2)
                canvas:
                    Color:
                        rgba: 1, 1, 1, 0.1
                    Rectangle:
                        pos: self.pos
                        size: self.size

            Label:
                text: "--- ROBOT ---"
                bold: True
                color: 0.5, 0.7, 1, 1
                size_hint_y: None
                height: dp(30)

            ScrollView:
                size_hint_y: 0.5
                BoxLayout:
                    id: queue_list
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(8)

<SettingsScreen>:
    name: "settings"
    BoxLayout:
        orientation: "vertical"
        padding: dp(40)
        spacing: dp(20)
        canvas.before:
            Color:
                rgb: 0.08, 0.08, 0.12
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "CONFIGURATION IP"
            font_size: "24sp"
            bold: True
            size_hint_y: None
            height: dp(60)

        TextInput:
            id: ip_input
            text: "127.0.0.1"
            multiline: False
            size_hint_y: None
            height: dp(50)
            font_size: "18sp"

        StyledButton:
            text: "ENREGISTRER"
            size_hint_y: None
            height: dp(60)
            background_color: 0.1, 0.6, 0.3, 1
            on_press: root.save_config(ip_input.text)
        
        StyledButton:
            text: "RETOUR"
            size_hint_y: None
            height: dp(60)
            background_color: 0.6, 0.2, 0.2, 1
            on_press: app.root.current = "main"
        
        Widget:
'''

if __name__ == "__main__":
    RobotApp().run()