import tkinter as tk
import asyncio
import threading
import websockets
import random

ROBOT_IP = "10.42.0.1"
PORT = 8765
PASSWORD = "2403"   


class SlayBotUI:
    def __init__(self, root):
        self.root = root

        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.config(bg="#000", cursor="none")

        self.ws = None
        self.loop = None
        self.connected = False

        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()

        self.tx = self.w / 2
        self.ty = self.h / 2
        self.sx = self.w / 2
        self.sy = self.h / 2

        # états
        self.state = "idle"  # idle = attend
        self.eye_open = True

        self.canvas = tk.Canvas(root, bg="#000", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.label = tk.Label(root, text="PRÊT", fg="white", bg="#000",
                              font=("Arial", 34, "bold"))
        self.label.place(relx=0.5, rely=0.08, anchor="center")

        # STOP
        self.btn_stop = tk.Button(root, text="STOP",
                                 bg="red", fg="white",
                                 font=("Arial", 22, "bold"),
                                 command=self.emergency)
        self.btn_stop.place(relx=0.5, rely=0.9, anchor="center")

        # CONFIRM
        self.btn_confirm = tk.Button(root, text="CONFIRMER",
                                    bg="green", fg="white",
                                    font=("Arial", 20, "bold"),
                                    command=self.confirm)

        # SETTINGS
        self.btn_settings = tk.Button(root, text="⚙",
                                     font=("Arial", 18),
                                     command=self.open_settings)
        self.btn_settings.place(x=20, y=20)

        self.root.bind("<Motion>", self.on_touch)

        self.loop_render()
        self.loop_blink()

    # ---------------- TOUCH ----------------
    def on_touch(self, e):
        self.tx = e.x
        self.ty = e.y

    # ---------------- BLINK ----------------
    def loop_blink(self):
        self.eye_open = False
        self.root.after(120, self.open_eye)

    def open_eye(self):
        self.eye_open = True
        self.root.after(random.randint(2000, 4000), self.loop_blink)

    # ---------------- SMOOTH ----------------
    def smooth(self):
        self.sx += (self.tx - self.sx) * 0.08
        self.sy += (self.ty - self.sy) * 0.08

    # ---------------- RENDER ----------------
    def loop_render(self):
        self.canvas.delete("all")
        self.smooth()

        cx = self.w/2
        cy = self.h/3


        colors = {
            "idle": "#00ffaa",        # attend
            "moving": "#ffd400",
            "happy": "#00ff66",
            "impatient": "#ff8800",
            "error": "#ff4444",
            "emergency": "#ff0000",
            "sad": "#3399ff",         # pas connecté
            "dead": "#555555"         # STOP
        }

        # état automatique si pas connecté
        if not self.connected:
            self.state = "sad"

        color = colors.get(self.state, "#ffffff")

        # yeux
        if self.state == "dead":
            self.draw_x(cx-140, cy, color)
            self.draw_x(cx+140, cy, color)

        elif self.eye_open:
            self.canvas.create_oval(cx-180, cy,
                                    cx-90, cy+90,
                                    fill=color)

            self.canvas.create_oval(cx+90, cy,
                                    cx+180, cy+90,
                                    fill=color)

        # bouche
        self.draw_mouth(cx, cy, color)

        self.root.after(16, self.loop_render)

    # ---------------- MOUTH ----------------
    def draw_mouth(self, cx, cy, color):
        y = self.h/2

        if self.state == "idle":
            self.canvas.create_line(cx-100, y+70, cx+100, y+70,
                                    fill=color, width=6)

        elif self.state == "moving":
            self.canvas.create_oval(cx-50, y, cx+50, y+80,
                                    fill=color)

        elif self.state == "happy":
            self.canvas.create_arc(cx-160, y, cx+160, y+160,
                                   start=0, extent=-180,
                                   fill=color)

        elif self.state == "sad":
            self.canvas.create_arc(cx-120, y+80, cx+120, y,
                                   start=0, extent=180,
                                   outline=color, width=6)

        elif self.state == "error":
            self.canvas.create_rectangle(cx-100, y+70, cx+100, y+90,
                                         fill=color)

        elif self.state == "dead":
            self.canvas.create_line(cx-120, y+80, cx+120, y+80,
                                    fill=color, width=8)

    # ---------------- X EYES ----------------
    def draw_x(self, x, y, color):
        self.canvas.create_line(x-40, y-40, x+40, y+40, fill=color, width=10)
        self.canvas.create_line(x-40, y+40, x+40, y-40, fill=color, width=10)

    # ---------------- ACTIONS ----------------
    def confirm(self):
        if self.ws:
            asyncio.run_coroutine_threadsafe(
                self.ws.send("status/received"), self.loop)

        self.state = "idle"
        self.btn_confirm.place_forget()

    def emergency(self):
        if self.ws:
            asyncio.run_coroutine_threadsafe(
                self.ws.send("emergency_stop"), self.loop)

        self.state = "dead"  

    # ---------------- SETTINGS ----------------
    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.geometry("300x250")
        win.title("Settings")

        tk.Label(win, text="Mot de passe").pack()

        entry = tk.Entry(win, show="*")
        entry.pack()

        def validate():
            if entry.get() == PASSWORD:
                tk.Button(win, text="Reconnecter",
                          command=lambda: threading.Thread(target=self.start_ws, daemon=True).start()
                          ).pack(pady=10)

        tk.Button(win, text="Valider", command=validate).pack(pady=5)

        tk.Button(win, text="Fermer UI", command=self.root.destroy).pack()

    # ---------------- WS ----------------
    async def listen(self):
        while True:
            try:
                async with websockets.connect(f"ws://{ROBOT_IP}:{PORT}") as ws:
                    self.ws = ws
                    self.connected = True

                    async for msg in ws:
                        msg = msg.lower()

                        if "deplacement" in msg:
                            self.state = "moving"

                        elif "arrived/table" in msg:
                            self.state = "happy"
                            self.btn_confirm.place(relx=0.5, rely=0.75, anchor="center")

                        elif "arrived/bar" in msg:
                            self.state = "idle"
                            self.btn_confirm.place_forget()

                        elif "error" in msg:
                            self.state = "error"

            except:
                self.connected = False
                self.state = "sad"
                await asyncio.sleep(3)

    def start_ws(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.listen())


# ---------------- MAIN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SlayBotUI(root)

    threading.Thread(target=app.start_ws, daemon=True).start()

    root.mainloop()