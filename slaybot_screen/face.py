import tkinter as tk
from tkinter import messagebox
import asyncio
import threading
import websockets
import random

# --- CONFIGURATION ---
SERVER_IP = "10.42.0.1"  
PORT = 8765
ADMIN_PASSWORD = "2403"

class SlayBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SlayBot OS - v2.0")

        # --- Setup Plein Écran ---
        self.root.configure(bg="#050505")
        self.root.overrideredirect(True) 
        
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.w}x{self.h}+0+0")
        self.root.attributes("-topmost", True)
        
        self.root.bind("<Escape>", self.exit_fs)
        self.root.config(cursor="none") 

        # État & Réseau
        self.ws = None
        self.loop = None
        self.connected = False
        self.state = "idle" 

        # Animation vars
        self.tx, self.ty = self.w / 2, self.h / 2 
        self.sx, self.sy = self.w / 2, self.h / 2 
        self.eye_height_mult = 1.0
        self.anim_counter = 0
        
        # UI Canvas
        self.canvas = tk.Canvas(root, bg="#050505", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        # Statut (Design épuré)
        self.status_label = tk.Label(root, text="● SYSTEM READY", fg="#111", bg="#050505", font=("Fixedsys", 10))
        self.status_label.place(relx=0.5, rely=0.98, anchor="s")

        # Zone invisible pour réglages (Haut Gauche)
        self.btn_settings = tk.Button(root, bg="#050505", activebackground="#050505", 
                                      bd=0, command=self.show_numpad, width=5, height=2)
        self.btn_settings.place(x=0, y=0)

        # Bouton STOP discret mais accessible
        self.btn_stop = tk.Button(root, text="✕", bg="#050505", fg="#300",
                                  activebackground="#500", activeforeground="#fff",
                                  font=("Arial", 14, "bold"), bd=0, command=self.emergency)
        self.btn_stop.place(relx=1.0, rely=0.0, anchor="ne", width=40, height=40)

        self.root.bind("<Motion>", self.on_touch)
        
        self.loop_render()
        self.loop_blink()

    def exit_fs(self, event=None):
        self.root.overrideredirect(False)
        self.root.attributes("-fullscreen", False)
        self.root.config(cursor="arrow")

    # --- ADMINISTRATION ---
    def show_numpad(self):
        self.root.config(cursor="arrow")
        self.numpad = tk.Toplevel(self.root)
        self.numpad.geometry(f"300x400+{int(self.w/2-150)}+{int(self.h/2-200)}")
        self.numpad.configure(bg="#0a0a0a", bd=2, relief="flat")
        self.numpad.overrideredirect(True) 
        self.numpad.attributes("-topmost", True)
        
        self.pass_var = tk.StringVar()
        tk.Label(self.numpad, textvariable=self.pass_var, font=("Courier", 30), bg="#000", fg="#0f2").pack(fill="x", pady=10)

        grid = tk.Frame(self.numpad, bg="#0a0a0a")
        grid.pack(expand=True, fill="both")

        btns = ['7','8','9','4','5','6','1','2','3','C','0','OK']
        for i, b in enumerate(btns):
            tk.Button(grid, text=b, font=("Arial", 15), bg="#151515", fg="white", bd=0,
                      command=lambda x=b: self.numpad_click(x)).grid(row=i//3, column=i%3, sticky="nsew", padx=2, pady=2)
        
        for i in range(3): grid.columnconfigure(i, weight=1)
        for i in range(4): grid.rowconfigure(i, weight=1)

    def numpad_click(self, char):
        curr = self.pass_var.get()
        if char == 'C': self.pass_var.set("")
        elif char == 'OK':
            if curr == ADMIN_PASSWORD:
                self.numpad.destroy()
                self.root.destroy()
            else:
                self.pass_var.set("ERR")
                self.root.after(500, lambda: self.pass_var.set(""))
        else:
            if len(curr) < 4: self.pass_var.set(curr + char)

    # --- RENDU VISUEL ---
    def on_touch(self, e):
        self.tx, self.ty = e.x, e.y

    def loop_blink(self):
        if self.state not in ["error", "emergency"]:
            self.eye_height_mult = 0.05
            self.root.after(120, lambda: setattr(self, "eye_height_mult", 1.0))
        self.root.after(random.randint(3000, 7000), self.loop_blink)

    def loop_render(self):
        self.canvas.delete("all")
        self.anim_counter += 1
        
        # Lissage du regard
        self.sx += (self.tx - self.sx) * 0.1
        self.sy += (self.ty - self.sy) * 0.1
        
        cx, cy = self.w / 2, self.h / 2
        scale = min(self.w, self.h) / 800

        palette = {
            "idle": "#00dfff", "moving": "#ffee00", "happy": "#00ffaa", 
            "error": "#ff3333", "emergency": "#ff0000"
        }
        color = palette.get(self.state, "#fff")
        
        self.status_label.config(text="● " + self.state.upper(), fg=color if self.connected else "#222")

        # --- YEUX ---
        e_space, e_w, e_h = 150 * scale, 80 * scale, 100 * scale
        
        for side in [-1, 1]:
            ex, ey = cx + (side * e_space), cy - 30 * scale
            
            if self.state in ["error", "emergency"]:
                # Yeux en X
                sz = 35 * scale
                self.canvas.create_line(ex-sz, ey-sz, ex+sz, ey+sz, fill=color, width=10*scale, capstyle="round")
                self.canvas.create_line(ex+sz, ey-sz, ex-sz, ey+sz, fill=color, width=10*scale, capstyle="round")
            else:
                # Forme de l'œil
                h_anim = e_h * self.eye_height_mult
                self.canvas.create_oval(ex-e_w, ey-h_anim, ex+e_w, ey+h_anim, outline=color, width=int(6*scale))
                
                # Pupille mobile
                if self.eye_height_mult > 0.5:
                    dx = (self.sx - ex) * 0.1
                    dy = (self.sy - ey) * 0.1
                    self.canvas.create_oval(ex+dx-25*scale, ey+dy-25*scale, ex+dx+25*scale, ey+dy+25*scale, fill=color)

        # --- BOUCHE ---
        m_y = cy + 140 * scale
        if self.state == "happy":
            self.canvas.create_arc(cx-80*scale, m_y-40*scale, cx+80*scale, m_y+40*scale, 
                                   start=0, extent=-180, outline=color, width=int(6*scale), style="arc")
        elif self.state == "moving":
            # Petite bouche "O" qui pulse
            r = (15 + random.randint(0,5)) * scale
            self.canvas.create_oval(cx-r, m_y-r, cx+r, m_y+r, outline=color, width=3*scale)
        else:
            # Trait horizontal simple
            self.canvas.create_line(cx-40*scale, m_y, cx+40*scale, m_y, fill=color, width=int(4*scale), capstyle="round")

        self.root.after(16, self.loop_render)

    # --- LOGIQUE RÉSEAU ---
    def set_state(self, s): 
        self.state = s

    def emergency(self): 
        self.set_state("emergency")
        self.send_to_ws("STOP")

    def send_to_ws(self, msg):
        if self.ws and self.connected:
            self.loop.call_soon_threadsafe(lambda: asyncio.ensure_future(self.ws.send(msg)))

    async def listen(self):
        uri = f"ws://{SERVER_IP}:{PORT}"
        while True:
            try:
                async with websockets.connect(uri, ping_interval=5) as ws:
                    self.ws, self.connected = ws, True
                    async for msg in ws:
                        m = msg.lower()
                        if "moving" in m: self.set_state("moving")
                        elif "arrived" in m: self.set_state("happy")
                        elif "error" in m: self.set_state("error")
                        else: self.set_state("idle")
            except:
                self.connected = False
                await asyncio.sleep(3) 

    def start_ws_thread(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.listen())

if __name__ == "__main__":
    root = tk.Tk()
    app = SlayBotUI(root)
    threading.Thread(target=app.start_ws_thread, daemon=True).start()
    root.mainloop()