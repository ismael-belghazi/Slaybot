import tkinter as tk
from tkinter import simpledialog, messagebox
import asyncio
import threading
import websockets
import random
import sys
import math

# --- CONFIGURATION ---
ROBOT_IP = "10.42.0.1"
PORT = 8765
PASSWORD = "2403"

class SlayBotUI:
    def __init__(self, root):
        self.root = root
        
        # Mode Kiosque
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.w}x{self.h}+0+0")
        self.root.attributes("-fullscreen", True)
        self.root.config(bg="#000", cursor="none")

        # État
        self.ws = None
        self.loop = None
        self.connected = False
        self.state = "idle"
        
        # Animation & Suivi (Lissage)
        self.tx, self.ty = self.w / 2, self.h / 2 # Cible
        self.sx, self.sy = self.w / 2, self.h / 2 # Position actuelle lissée
        self.eye_height_mult = 1.0  # Pour le clignement (1.0 ouvert, 0.1 fermé)

        self.canvas = tk.Canvas(root, bg="#000", highlightthickness=0, width=self.w, height=self.h)
        self.canvas.pack(fill="both", expand=True)

        # UI
        self.label = tk.Label(root, text="INITIALISATION", fg="white", bg="#000", font=("Arial", 28, "bold"))
        self.label.place(relx=0.5, rely=0.1, anchor="center")

        self.btn_stop = tk.Button(root, text="STOP D'URGENCE", bg="#ff0000", fg="white", font=("Arial", 20, "bold"),
                                 padx=20, pady=10, command=self.emergency)
        self.btn_stop.place(relx=0.5, rely=0.9, anchor="center")

        self.btn_confirm = tk.Button(root, text="CONFIRMER RÉCEPTION", bg="#00ff66", fg="black", font=("Arial", 18, "bold"),
                                    command=self.confirm)

        # Events
        self.root.bind("<Motion>", self.on_touch)
        
        # Start Loops
        self.loop_render()
        self.loop_blink()

    def on_touch(self, e):
        self.tx, self.ty = e.x, e.y

    def loop_blink(self):
        # Animation de clignement fluide
        self.eye_height_mult = 0.1
        self.root.after(100, self.open_eye)

    def open_eye(self):
        self.eye_height_mult = 1.0
        self.root.after(random.randint(3000, 6000), self.loop_blink)

    def smooth_motion(self):
        # Lissage du mouvement (Interpolation linéaire)
        self.sx += (self.tx - self.sx) * 0.1
        self.sy += (self.ty - self.sy) * 0.1

    def loop_render(self):
        self.canvas.delete("all")
        self.smooth_motion()
        
        cx, cy = self.w / 2, self.h / 2 - 50
        
        colors = {
            "idle": "#00d4ff", "moving": "#ffd400", "happy": "#00ff66",
            "error": "#ff4444", "emergency": "#ff0000", "sad": "#3399ff", "dead": "#555555"
        }
        color = colors.get(self.state, "#ffffff")
        
        # Mise à jour du label
        status_text = "CONNECTÉ" if self.connected else "DÉCONNECTÉ"
        self.label.config(text=status_text, fg=color)

        # --- DESSIN DES YEUX ---
        eye_spacing = 160
        eye_size = 100
        
        for side in [-1, 1]: # Gauche et Droite
            ex = cx + (side * eye_spacing)
            ey = cy
            
            if self.state == "dead":
                self.draw_x(ex, ey, color)
            elif self.state == "happy":
                # Yeux en forme de ^ ^
                self.canvas.create_arc(ex-60, ey-40, ex+60, ey+60, start=0, extent=180, outline=color, width=15, style="arc")
            else:
                # Globe oculaire
                h = eye_size * self.eye_height_mult
                self.canvas.create_oval(ex-eye_size, ey-h, ex+eye_size, ey+h, fill="white", outline=color, width=2)
                
                # Pupille (suit le mouvement sx, sy)
                if self.eye_height_mult > 0.5:
                    dx = (self.sx - ex) * 0.15 # Amplitude mouvement pupille
                    dy = (self.sy - ey) * 0.15
                    self.canvas.create_oval(ex+dx-30, ey+dy-30, ex+dx+30, ey+dy+30, fill="#000")

        # --- DESSIN DE LA BOUCHE ---
        self.draw_mouth(cx, cy + 180, color)
        
        self.root.after(16, self.loop_render) # ~60 FPS

    def draw_mouth(self, mx, my, color):
        if self.state == "happy":
            # Grand sourire
            self.canvas.create_arc(mx-150, my-100, mx+150, my+100, start=0, extent=-180, fill=color, outline="")
        elif self.state in ["error", "sad"]:
            # Triste
            self.canvas.create_arc(mx-100, my, mx+100, my+100, start=0, extent=180, outline=color, width=8, style="arc")
        elif self.state == "moving":
            # Bouche en O (étonné/concentré)
            self.canvas.create_oval(mx-40, my-20, mx+40, my+60, outline=color, width=6)
        else:
            # Neutre (ligne arrondie)
            self.canvas.create_line(mx-80, my+20, mx+80, my+20, fill=color, width=8, capstyle="round")

    def draw_x(self, x, y, color):
        size = 50
        self.canvas.create_line(x-size, y-size, x+size, y+size, fill=color, width=12)
        self.canvas.create_line(x-size, y+size, x+size, y-size, fill=color, width=12)

    # ---------------- ACTIONS & WS (Identique à ton code avec ajustements mineurs) ----------------
    def set_state(self, new_state):
        self.state = new_state

    def emergency(self):
        self.set_state("dead")
        if self.ws:
            asyncio.run_coroutine_threadsafe(self.ws.send("emergency_stop"), self.loop)

    def confirm(self):
        self.set_state("idle")
        self.btn_confirm.place_forget()
        if self.ws:
            asyncio.run_coroutine_threadsafe(self.ws.send("status/received"), self.loop)

    async def listen(self):
        uri = f"ws://{ROBOT_IP}:{PORT}"
        while True:
            try:
                async with websockets.connect(uri, ping_interval=5) as ws:
                    self.ws = ws
                    self.connected = True
                    async for msg in ws:
                        m = msg.lower()
                        if "deplacement" in m: self.set_state("moving")
                        elif "arrived/table" in m: 
                            self.set_state("happy")
                            self.btn_confirm.place(relx=0.5, rely=0.75, anchor="center")
                        elif "error" in m: self.set_state("error")
                        elif "idle" in m: self.set_state("idle")
            except:
                self.connected = False
                await asyncio.sleep(3)

    def start_ws(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.listen())

if __name__ == "__main__":
    root = tk.Tk()
    app = SlayBotUI(root)
    threading.Thread(target=app.start_ws, daemon=True).start()
    root.mainloop()