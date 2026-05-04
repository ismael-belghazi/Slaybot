import tkinter as tk
import asyncio
import threading
import websockets
import random
import time
import math

# --- CONFIGURATION ---
SERVER_IP = "10.42.0.1"
PORT = 8765
ADMIN_PASSWORD = "2403"
VERSION = "v3.1-MHI-INC"

class SlayBotTactical:
    def __init__(self, root):
        self.root = root
        self.root.title(f"SLAYBOT_OS_{VERSION}")
        
        # --- Fullscreen Terminal Mode ---
        self.root.configure(bg="#000500")
        self.root.overrideredirect(True)
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.w}x{self.h}+0+0")
        self.root.attributes("-topmost", True)
        self.root.config(cursor="none")
        self.pulse_val=0
        self.pulse_dir=1
        # System State
        self.ws = None
        self.loop = None # Sera défini dans start_network
        self.connected = False
        self.state = "booting"
        self.boot_logs = []
        self.boot_progress = 0
        self.eye_height = 1.0

        self.canvas = tk.Canvas(root, bg="#000500", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        # Lancement des processus
        threading.Thread(target=self.run_boot, daemon=True).start()
        
        # Bindings
        self.canvas.bind("<Button-1>", self.handle_click)
        
        self.update_ui()
        self.blink_logic()

    # --- LOGIQUE DE BOOT (COMPLÈTE) ---
    def run_boot(self):
        # Phase 1 : Le boot qui va crash
        log_msgs_1 = [
            "INITIALIZING KERNEL_V4.2...",
            "CHECKING RAM_INTEGRITY... OK",
            "LOADING NEURAL_DRIVERS... DONE",
            "MOUNTING /DEV/SERIAL_0... OK",
            "BYPASSING SECURITY_PROTOCOL... DONE",
            "ERROR: MODULE_BERCHE DETECTED",
            "ENABLING TACTICAL_HUD_V3...",
            "DELETING MODULE_BERCHE... [OK]",
            "CRITICAL ERROR: BLUE BUTTON PRESSED BY USER:Marie",
            "REBOOTING SYSTEM..."
        ]

        for msg in log_msgs_1:
            self.boot_logs.append(f"[SYS] {msg}")
            if len(self.boot_logs) > 8: self.boot_logs.pop(0)
            speed = random.uniform(0.04, 0.12)
            for _ in range(10):
                self.boot_progress += 0.5
                time.sleep(speed)
            
            if "REBOOTING" in msg:
                time.sleep(1)
                self.boot_logs = []
                self.boot_progress = 0
                time.sleep(1.5)
                break

        # Phase 2 : Recovery
        self.boot_logs.append("[!] RECOVERY MODE ACTIVE")
        log_msgs_2 = [
            "RE-SYNCING SERVO_MOTORS...",
            "RE-ESTABLISHING CORE_LINK...",
            "SCANNING FOR CORE_SERVER..."
        ]

        for msg in log_msgs_2:
            self.boot_logs.append(f"[SYS] {msg}")
            for _ in range(10):
                self.boot_progress += 2.5
                time.sleep(0.04)

        time.sleep(1.5)
        self.boot_progress = 100
        self.boot_logs.append("[!] BOOT COMPLETE. STARTING OS...")
        time.sleep(1)
        self.state = "idle"

    # --- GESTION RÉSEAU ---
    async def listen(self):
            uri = f"ws://{SERVER_IP}:{PORT}"
            while True:
                try:
                    async with websockets.connect(uri) as ws:
                        self.ws = ws
                        self.connected = True
                        await ws.send("STATUS/TACTICAL_CONNECTED")
                        async for msg in ws:
                            m = msg.lower()
                            print(f"Received: {m}") 

                            # Correction des conditions de détection
                            if "go/table" in m or "clean/table" in m or "statut: deplacement" in m:
                                self.state = "moving"
                                                        
                            elif "arrived" in m or "arrivé" in m:
                                    if "bar" in m:
                                        self.state = "idle" 
                                    else:
                                        self.state = "arrived" 
                            elif "emergency" in m:
                                            self.state = "emergency"
                                
                except Exception as e:
                    print(f"Erreur connexion: {e}")
                    self.connected = False
                    self.ws = None
                    await asyncio.sleep(2)

    def start_network(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.listen())


    def emergency_shutdown(self):
        if self.ws and self.loop:
            asyncio.run_coroutine_threadsafe(
                self.ws.send("[WARNING] !!! EMERGENCY STOP !!!"), 
                self.loop
            )
        self.trigger_emergency_ui()

    def confirm_reception(self):
            if self.ws and self.loop:
                asyncio.run_coroutine_threadsafe(
                    self.ws.send("status/received"), 
                    self.loop
                )
            self.state = "idle" 
            
    def handle_click(self, event):
            # On définit le scale ici aussi pour que les calculs de collision fonctionnent
            scale = self.h / 1000 
            if self.state == "emergency":
                self.state = "idle"
                print("[SYS] EMERGENCY RESET BY OPERATOR")
                return

            # Bouton Paramètres (Bas Droite)
            if event.x > self.w - 100 and event.y > self.h - 100:
                self.show_numpad()
                
            # Bouton Arrêt Urgence (Haut Droite)
            elif event.x > self.w - 120 and event.y < 80:
                self.state = "emergency"
                if self.ws:
                    asyncio.run_coroutine_threadsafe(self.ws.send("emergency_stop"), self.loop)
            
            # Bouton Réception (Zone Mallette / Bouton Tactique)
            elif self.state == "arrived":
                cx, cy = self.w/2, self.h/2
                my = cy + 150 * scale
                bw, bh = 240 * scale, 70 * scale # Doit être identique à draw_face
            if cx-bw < event.x < cx+bw and my+20 < event.y < my+20+bh:
                self.confirm_reception()

    def show_numpad(self):
        self.root.config(cursor="arrow")
        win = tk.Toplevel(self.root)
        win.geometry("300x450")
        win.configure(bg="#000")
        win.overrideredirect(True)
        win.geometry(f"+{int(self.w/2-150)}+{int(self.h/2-225)}")
        
        entry_var = tk.StringVar()
        tk.Label(win, textvariable=entry_var, font=("Courier", 24), bg="#000", fg="#0f0").pack(pady=10)
        
        def press(k):
            if k == 'EXIT': win.destroy(); self.root.config(cursor="none")
            elif k == 'OFF' and entry_var.get() == ADMIN_PASSWORD: self.root.destroy()
            elif k == 'C': entry_var.set("")
            else: entry_var.set(entry_var.get() + k)

        frame = tk.Frame(win, bg="#000")
        frame.pack()
        btns = ['7','8','9','4','5','6','1','2','3','C','0','OFF']
        for i, b in enumerate(btns):
            tk.Button(frame, text=b, width=5, height=2, bg="#001100", fg="#0f0", font=("Courier", 12, "bold"),
                      command=lambda x=b: press(x)).grid(row=i//3, column=i%3, padx=5, pady=5)
        
        tk.Button(win, text="[ CLOSE UI ]", bg="#300", fg="red", command=lambda: press('EXIT')).pack(fill="x", pady=10)

    # --- DESSIN & UI ---
# --- DESSIN & UI (VERSION STABLE) ---
    def update_ui(self):
        try:
            self.canvas.delete("all")
            cx, cy = self.w/2, self.h/2

            # 1. Scanlines CRT (Fond)
            for i in range(0, self.h, 4):
                self.canvas.create_line(0, i, self.w, i, fill="#000700")

            # 2. Effet Radar (Sécurisé sans stipple)
            # On utilise une ligne avec une couleur très sombre pour simuler le scan
            scan_y = (time.time() * 150) % self.h
            self.canvas.create_line(0, scan_y, self.w, scan_y, fill="#003300", width=2)

            if self.state == "booting":
                self.draw_boot_screen(cx, cy)
            else:
                self.draw_tactical_hud(cx, cy)
                self.draw_face(cx, cy)
                self.draw_tactical_buttons()

        except Exception as e:
            # Si ça plante, on l'affiche en console mais on ne stoppe pas le programme
            print(f"UI DRAW ERROR: {e}")
        
        # On relance quoi qu'il arrive
        self.root.after(16, self.update_ui)

    def draw_boot_screen(self, cx, cy):
        self.canvas.create_text(cx, cy-120, text="--- SLAYBOT MIL-SPEC BOOT ---", fill="#0f0", font=("Courier", 20, "bold"))
        self.canvas.create_rectangle(cx-200, cy-20, cx+200, cy, outline="#0f0")
        self.canvas.create_rectangle(cx-200, cy-20, cx-200 + (4*self.boot_progress), cy, fill="#0f0")
        for i, log in enumerate(self.boot_logs):
            self.canvas.create_text(cx, cy+50+(i*20), text=log, fill="#0f0", font=("Courier", 10))

    def draw_tactical_hud(self, cx, cy):
        color = "#0f0" if (self.connected and self.state != "emergency") else "#f00"
        d, s = 200, 40
        # Coins de visée
        self.canvas.create_line(cx-d, cy-d, cx-d+s, cy-d, fill=color, width=2)
        self.canvas.create_line(cx-d, cy-d, cx-d, cy-d+s, fill=color, width=2)
        self.canvas.create_line(cx+d, cy+d, cx+d-s, cy+d, fill=color, width=2)
        self.canvas.create_line(cx+d, cy+d, cx+d, cy+d-s, fill=color, width=2)
        
        status = "CORE_LINK: STABLE" if self.connected else "CORE_LINK: LOST - ANGRY_MODE"
        if self.state == "emergency": status = "CRITICAL: EMERGENCY_STOP_ACTIVE"
        
        self.canvas.create_text(20, self.h-30, text=f"> {status} | {self.state.upper()} | {VERSION}", fill=color, anchor="w", font=("Courier", 12))

    def draw_face(self, cx, cy):
        scale = self.h / 1000
        color = "#0f0" if (self.connected and self.state != "emergency") else "#f00"
        glow_color = "#001a00" if color == "#0f0" else "#1a0000"
        
        # Animation pulse ultra-simplifiée pour éviter les erreurs de calcul
        self.pulse_val += 4 * self.pulse_dir
        if self.pulse_val > 100 or self.pulse_val < 0: self.pulse_dir *= -1
        
        # Yeux
        for side in [-1, 1]:
            ex, ey = cx + (side * 160 * scale), cy - 40 * scale
            h = 80 * scale * self.eye_height
            # Lueur (Cercle plus large et sombre dessous)
            self.canvas.create_oval(ex-65*scale, ey-h-5, ex+65*scale, ey+h+5, outline=glow_color, width=5)
            # Principal
            self.canvas.create_oval(ex-60*scale, ey-h, ex+60*scale, ey+h, outline=color, width=3)
            if self.eye_height > 0.5:
                self.canvas.create_oval(ex-15*scale, ey-15*scale, ex+15*scale, ey+15*scale, fill=color)

        # Bouche / Bouton Confirmation
        my = cy + 150 * scale
        if self.state == "arrived":
            bw, bh = 240 * scale, 70 * scale
            # Fond bouton
            self.canvas.create_rectangle(cx-bw, my+20, cx+bw, my+20+bh, outline=color, width=4, fill="#000800")
            
            # Texte (On simplifie la couleur pour éviter le crash de formatage hex)
            self.canvas.create_text(cx, my+20+(bh/2), 
                                    text=">> CONFIRM SYSTEM <<", 
                                    fill=color, font=("Courier", int(18*scale), "bold"))
            
            # Décorations (Lignes tactiques)
            self.canvas.create_line(cx-bw-30, my+20+bh/2, cx-bw, my+20+bh/2, fill=color, width=2)
            self.canvas.create_line(cx+bw+30, my+20+bh/2, cx+bw, my+20+bh/2, fill=color, width=2)
            
        elif color == "#f00": # Mode Urgence ou Déconnecté
            points = [cx-60*scale, my, cx-30*scale, my+20*scale, cx, my, cx+30*scale, my+20*scale, cx+60*scale, my]
            self.canvas.create_line(points, fill=color, width=5, capstyle="round")
        else: # Mode IDLE (Simple ligne avec lueur)
            self.canvas.create_line(cx-50*scale, my, cx+50*scale, my, fill=glow_color, width=10)
            self.canvas.create_line(cx-50*scale, my, cx+50*scale, my, fill=color, width=4)
    
    def draw_tactical_buttons(self):
        # Bouton Paramètres (CMD)
        self.canvas.create_rectangle(self.w-70, self.h-70, self.w-20, self.h-20, outline="#0f0", width=2)
        self.canvas.create_text(self.w-45, self.h-45, text="CMD", fill="#0f0", font=("Courier", 10, "bold"))
        
        # Bouton Arrêt Urgence (KILL_SW)
        self.canvas.create_rectangle(self.w-110, 20, self.w-20, 70, outline="red", width=2)
        self.canvas.create_text(self.w-65, 45, text="KILL_SW", fill="red", font=("Courier", 10, "bold"))

    def blink_logic(self):
        if self.state != "booting" and self.state != "emergency":
            self.eye_height = 0.1
            self.root.after(150, lambda: setattr(self, 'eye_height', 1.0))
        self.root.after(random.randint(3000, 6000), self.blink_logic)

# --- EXECUTION ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SlayBotTactical(root)
    # Lancement du réseau dans un thread séparé avec gestion de la loop
    threading.Thread(target=app.start_network, daemon=True).start()
    root.mainloop()