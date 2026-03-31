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
    """
    Interface de communication asynchrone. 
    Le thread réseau est séparé pour éviter de bloquer l'UI Kivy.
    """
    ws = None
    online = False
    callback = None
    robot_ip = "127.0.0.1"
    port = 8765

    @staticmethod
    def connect():
        """ Initialise la connexion et définit les handlers d'événements réseau. """
        if RobotAPI.ws:
            RobotAPI.ws.close()

        def on_msg(ws, message):
            msg = message.strip().lower()
            # Utilisation de Clock.schedule_once pour interagir avec l'UI depuis un thread esclave
            if "arrived/bar" in msg:
                if MainScreen.instance:
                    Clock.schedule_once(lambda dt: MainScreen.instance.on_mission_complete())
            elif "arrived/table" in msg:
                if RobotAPI.callback:
                    Clock.schedule_once(lambda dt: RobotAPI.callback("Robot à destination"))

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
        
        # Le daemon=True permet de tuer le thread réseau si l'app principale s'arrête
        threading.Thread(target=RobotAPI.ws.run_forever, daemon=True).start()

    @staticmethod
    def send(cmd):
        """ Envoie une commande brute au serveur si la connexion est active. """
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
    queue = ListProperty([])
    is_busy = False # Verrou logic pour empêcher l'envoi de commandes multiples

    def __init__(self, **kw):
        super().__init__(**kw)
        MainScreen.instance = self

    def on_enter(self):
        """ S'exécute à l'affichage de l'écran : définit le callback et l'automate. """
        RobotAPI.callback = self.set_status
        # Vérification cyclique de la file d'attente (toutes les secondes)
        Clock.schedule_interval(self.check_queue, 1)

    def set_status(self, text): 
        self.status = text

    def add_to_queue(self, table_id):
        """ Ajoute une mission à la liste si elle n'y figure pas déjà. """
        task = f"Table {table_id}"
        if task not in self.queue:
            self.queue.append(task)
            self.update_queue_ui()

    def remove_specific(self, task_name):
        """ Supprime une tâche de la liste et gère le déverrouillage si nécessaire. """
        if task_name in self.queue:
            # Si on supprime la tâche que le robot est en train de faire
            if self.queue.index(task_name) == 0 and self.is_busy:
                self.is_busy = False
            self.queue.remove(task_name)
            self.update_queue_ui()

    def update_queue_ui(self):
        """ Reconstruit dynamiquement la liste visuelle des missions (Scrollview). """
        container = self.ids.queue_list
        container.clear_widgets()
        for item in self.queue:
            line = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
            lbl = Label(text=item, halign='left', font_size='16sp')
            btn = Button(text="X", size_hint_x=None, width=dp(45), 
                         background_normal='', background_color=(0.8, 0.2, 0.2, 1))
            # Utilisation d'un argument par défaut (it=item) pour capturer la valeur dans la lambda
            btn.bind(on_release=lambda x, it=item: self.remove_specific(it))
            line.add_widget(lbl)
            line.add_widget(btn)
            container.add_widget(line)

    def on_mission_complete(self):
        """ Nettoyage suite au signal 'arrived/bar' envoyé par le simulateur. """
        if self.queue:
            self.queue.pop(0)
            self.update_queue_ui()
        self.is_busy = False
        self.status = "Prêt"

    def check_queue(self, dt):
        """ 
        Automate de contrôle : envoie l'ordre au robot 
        si une tâche existe et que le système n'est pas occupé. 
        """
        if self.queue and not self.is_busy and RobotAPI.online:
            next_table = self.queue[0].split()[-1]
            RobotAPI.send(f"go/{next_table}")
            self.is_busy = True
            self.status = f"En route : Table {next_table}"

    def reconnect(self):
        RobotAPI.connect()

# =============================================================================
# PERSISTANCE ET INITIALISATION
# =============================================================================
class SettingsScreen(Screen):
    def save_config(self, new_ip):
        """ Sauvegarde l'IP localement pour la réutiliser au prochain démarrage. """
        RobotAPI.robot_ip = new_ip
        with open(CONFIG_FILE, "w") as f:
            json.dump({"ip": new_ip}, f)
        RobotAPI.connect()
        self.manager.current = "main"

class RobotApp(App):
    def build(self):
        """ Initialisation de l'application et chargement des données. """
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                try:
                    data = json.load(f)
                    RobotAPI.robot_ip = data.get("ip", "127.0.0.1")
                except: pass
        
        RobotAPI.connect()
        return Builder.load_string(KV)

# --- Design et styles (Langage KV) ---
KV = '''
<StyledButton@Button>:
    background_normal: ''
    background_down: ''
    font_size: '18sp'
    bold: True
    canvas.before:
        Color:
            rgba: (self.background_color[0]*0.6, self.background_color[1]*0.6, self.background_color[2]*0.6, 1) if self.state == 'down' else self.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

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

        BoxLayout:
            orientation: "vertical"
            padding: dp(25)
            spacing: dp(15)

            Label:
                text: root.status
                font_size: "24sp"
                bold: True
                color: (0, 0.9, 0.5, 1) if "Connecté" in self.text or "route" in self.text else (0.9, 0.2, 0.2, 1)
                size_hint_y: None
                height: dp(60)

            GridLayout:
                cols: 2
                spacing: dp(20)
                StyledButton:
                    text: "TABLE 1"
                    background_color: 0.2, 0.4, 0.9, 1
                    on_press: root.add_to_queue("1")
                StyledButton:
                    text: "TABLE 2"
                    background_color: 0.9, 0.7, 0.1, 1
                    on_press: root.add_to_queue("2")
                StyledButton:
                    text: "TABLE 3"
                    background_color: 0.8, 0.1, 0.1, 1
                    on_press: root.add_to_queue("3")
                StyledButton:
                    text: "TABLE 4"
                    background_color: 0.1, 0.7, 0.2, 1
                    on_press: root.add_to_queue("4")

            Widget:
                size_hint_y: 1 

            BoxLayout:
                size_hint_y: None
                height: dp(65)
                spacing: dp(15)
                StyledButton:
                    text: "RECONNECTER"
                    background_color: 0.1, 0.5, 0.3, 1
                    on_press: root.reconnect()
                StyledButton:
                    text: "PARAMÈTRES"
                    background_color: 0.3, 0.3, 0.3, 1
                    on_press: app.root.current = "settings"

        BoxLayout:
            orientation: "vertical"
            size_hint_x: 0.45
            padding: dp(20)
            canvas.before:
                Color:
                    rgb: 0.14, 0.14, 0.18
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(20), 0, 0, dp(20)]

            Label:
                text: "MISSIONS EN COURS"
                bold: True
                font_size: '16sp'
                color: 0.7, 0.7, 0.7, 1
                size_hint_y: None
                height: dp(50)

            ScrollView:
                BoxLayout:
                    id: queue_list
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(12)

<SettingsScreen>:
    name: "settings"
    BoxLayout:
        orientation: "vertical"
        padding: dp(50)
        spacing: dp(25)
        canvas.before:
            Color:
                rgb: 0.08, 0.08, 0.12
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "PARAMÈTRES RÉSEAU"
            font_size: "26sp"
            bold: True
            size_hint_y: None
            height: dp(80)

        TextInput:
            id: ip_input
            text: "127.0.0.1"
            hint_text: "IP du Robot"
            multiline: False
            size_hint_y: None
            height: dp(55)
            font_size: "20sp"
            background_color: 0.15, 0.15, 0.2, 1
            foreground_color: 1, 1, 1, 1
            padding: [dp(15), dp(15)]

        BoxLayout:
            size_hint_y: None
            height: dp(65)
            spacing: dp(20)
            StyledButton:
                text: "ENREGISTRER"
                background_color: 0.1, 0.6, 0.3, 1
                on_press: root.save_config(ip_input.text)
            StyledButton:
                text: "RETOUR"
                background_color: 0.6, 0.2, 0.2, 1
                on_press: app.root.current = "main"
        
        Widget:
'''

if __name__ == "__main__":
    RobotApp().run()