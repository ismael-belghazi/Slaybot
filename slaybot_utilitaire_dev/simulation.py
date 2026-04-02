import sys
import asyncio
import threading
import socket
import websockets
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QTimer, QPointF

# -----------------------------------------------------------------------------
# CONFIGURATION ET CONSTANTES
# -----------------------------------------------------------------------------
SERVER_PORT = 8765
SPEED = 6 

TABLES = {
    "T1": QPointF(150, 100),
    "T2": QPointF(150, 300),
    "T3": QPointF(650, 100),
    "T4": QPointF(650, 300),
    "BAR": QPointF(400, 400)
}

TABLE_COLORS = {
    "T1": QColor(0, 102, 204),
    "T2": QColor(255, 204, 0),
    "T3": QColor(204, 0, 0),
    "T4": QColor(0, 204, 0),
    "BAR": QColor(102, 204, 255)
}

PATHS = {
    "T1": [TABLES["BAR"], QPointF(300, 250), TABLES["T1"]],
    "T2": [TABLES["BAR"], QPointF(300, 300), TABLES["T2"]],
    "T3": [TABLES["BAR"], QPointF(500, 250), TABLES["T3"]],
    "T4": [TABLES["BAR"], QPointF(500, 300), TABLES["T4"]],
    "BAR": [TABLES["BAR"]]
}

# -----------------------------------------------------------------------------
# CLASSE PRINCIPALE DU SIMULATEUR
# -----------------------------------------------------------------------------
class RobotSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulateur Robot Restaurant")
        self.setGeometry(100, 100, 800, 500)
        self.robot_pos = QPointF(TABLES["BAR"])
        self.queue = []  
        self.current_target = None
        self.path = []
        self.sending = False
        self.clients = set()
        self.arrived = False  

        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

        layout = QHBoxLayout(self)
        self.left_panel = QVBoxLayout()
        layout.addLayout(self.left_panel, 1)

        self.queue_label = QLabel("File d'attente : Vide")
        self.left_panel.addWidget(self.queue_label)
        self.ip_label = QLabel("IP serveur : Recherche...")
        self.left_panel.addWidget(self.ip_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_robot_logic)
        self.timer.start(30)

    def broadcast(self, message):
        for ws in self.clients.copy():
            try: asyncio.run_coroutine_threadsafe(ws.send(message), self.loop)
            except: pass

    def add_task(self, command):
        cmd = command.strip().lower()
        if "go/" in cmd:
            table_id = cmd.split("/")[-1].upper()
            table_name = f"T{table_id}" if not table_id.startswith("T") else table_id
            if table_name in PATHS and table_name not in self.queue:
                self.queue.append(table_name)
        elif "emergency" in cmd:
            self.queue.clear()
            self.path = []
            self.sending = False

    def update_robot_logic(self):
        if not self.sending and self.queue:
            self.current_target = self.queue[0]
            self.path = PATHS[self.current_target].copy()
            self.sending = True
            self.arrived = False

        if self.sending and self.path:
            self.move_step()
        elif self.sending and not self.path:
            if not self.arrived:
                self.arrived = True
                if self.current_target != "BAR":
                    self.broadcast(f"arrived/table/{self.current_target}")
                    self.show_validation_popup()
                else:
                    self.broadcast("arrived/bar")
                    self.sending = False

        self.update()

    def move_step(self):
        next_pt = self.path[0]
        dx = next_pt.x() - self.robot_pos.x()
        dy = next_pt.y() - self.robot_pos.y()
        dist = (dx**2 + dy**2)**0.5
        if dist < SPEED:
            self.robot_pos = QPointF(next_pt)
            self.path.pop(0)
        else:
            self.robot_pos.setX(self.robot_pos.x() + dx/dist * SPEED)
            self.robot_pos.setY(self.robot_pos.y() + dy/dist * SPEED)

    def show_validation_popup(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Livraison")
        msg.setText(f"Valider la livraison pour {self.current_target} ?")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(self.validation_done)
        msg.show()

    def validation_done(self):
            self.broadcast(f"validated/{self.current_target}")
            reverse_path = PATHS[self.current_target][::-1] 
            self.path = reverse_path
            if self.queue: self.queue.pop(0)
            self.current_target = "BAR"
            self.arrived = False
            self.sending = True

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        for name, path in PATHS.items():
            if name == "BAR": continue
            p.setPen(QPen(TABLE_COLORS[name], 2, Qt.DashLine))
            for i in range(len(path)-1):
                p.drawLine(path[i], path[i+1])

        for name, pos in TABLES.items():
            p.setBrush(QBrush(TABLE_COLORS[name]))
            p.setPen(Qt.black)
            p.drawEllipse(pos, 20, 20)
            p.drawText(int(pos.x())-10, int(pos.y())-25, name)

        p.setBrush(QBrush(QColor(50, 50, 50)))
        p.drawEllipse(self.robot_pos, 15, 15)
        self.queue_label.setText(f"File d'attente : {' -> '.join(self.queue) if self.queue else 'Vide'}")

# -----------------------------------------------------------------------------
# GESTION RÉSEAU ET SERVEUR WEBSOCKET
# -----------------------------------------------------------------------------
async def ws_handler(ws, path, sim):
    sim.clients.add(ws)
    try:
        async for msg in ws: sim.add_task(msg)
    except: pass
    finally: sim.clients.discard(ws)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def start_server(sim):
    local_ip = get_local_ip()
    sim.ip_label.setText(f"IP Serveur : ws://{local_ip}:{SERVER_PORT}")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    srv = websockets.serve(lambda ws, p: ws_handler(ws, p, sim), '0.0.0.0', SERVER_PORT)
    loop.run_until_complete(srv)
    loop.run_forever()

# -----------------------------------------------------------------------------
# POINT D'ENTRÉE DU PROGRAMME
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    sim = RobotSimulator()
    threading.Thread(target=start_server, args=(sim,), daemon=True).start()
    sim.show()
    sys.exit(app.exec_())