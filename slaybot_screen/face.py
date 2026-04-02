import tkinter as tk
import asyncio
import threading
import websockets

SERVER_IP = "10.42.0.1"
PORT = 8765

class SlayBotVisual:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.config(cursor="none", bg="#1a1a1a")
        self.ws = None 

        self.canvas = tk.Canvas(root, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.status_label = tk.Label(root, text="INITIALISATION...", font=("Arial", 24, "bold"), fg="white", bg="#1a1a1a")
        self.status_label.pack(side="bottom", pady=20)

        # Conteneur des boutons
        self.btn_frame = tk.Frame(root, bg="#1a1a1a")
        self.btn_frame.pack(side="bottom", pady=30)

        # Bouton Confirmer (Vert) - Caché au début
        self.btn_confirm = tk.Button(self.btn_frame, text="J'AI REÇU MA COMMANDE", font=("Arial", 20, "bold"),
                                    bg="#2ecc71", fg="white", command=self.send_confirm, height=3, width=25)
        
        # Bouton STOP (Rouge) - Toujours là
        self.btn_stop = tk.Button(self.btn_frame, text="STOP", font=("Arial", 20, "bold"),
                                 bg="#e74c3c", fg="white", command=self.send_emergency, height=3, width=10)
        
        self.btn_stop.pack(side="left", padx=20)

        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()
        self.set_face_happy()

    def send_confirm(self):
        if self.ws:
            asyncio.run_coroutine_threadsafe(self.ws.send("status/received"), self.loop)
            self.btn_confirm.pack_forget()

    def send_emergency(self):
        if self.ws:
            asyncio.run_coroutine_threadsafe(self.ws.send("status/emergency_stop"), self.loop)
        self.set_face_error("ARRÊT D'URGENCE ACTIVÉ")

    def draw_face(self, color, eye="normal", mouth="happy"):
        self.canvas.delete("all")
        y_eye = self.height * 0.35
        if eye == "normal":
            self.canvas.create_oval(self.width/2-200, y_eye-60, self.width/2-100, y_eye+60, fill=color, outline="")
            self.canvas.create_oval(self.width/2+100, y_eye-60, self.width/2+200, y_eye+60, fill=color, outline="")
        else: # Yeux en X
            self.canvas.create_line(self.width/2-200, y_eye-50, self.width/2-100, y_eye+50, fill=color, width=15)
            self.canvas.create_line(self.width/2-200, y_eye+50, self.width/2-100, y_eye-50, fill=color, width=15)
            self.canvas.create_line(self.width/2+100, y_eye-50, self.width/2+200, y_eye+50, fill=color, width=15)
            self.canvas.create_line(self.width/2+100, y_eye+50, self.width/2+200, y_eye-50, fill=color, width=15)

        y_mouth = self.height * 0.55
        if mouth == "happy":
            self.canvas.create_arc(self.width/2-120, y_mouth-60, self.width/2+120, y_mouth+60, start=0, extent=-180, fill=color, outline="")
        elif mouth == "wow":
            self.canvas.create_oval(self.width/2-50, y_mouth-50, self.width/2+50, y_mouth+50, fill=color, outline="")
        else:
            self.canvas.create_rectangle(self.width/2-100, y_mouth, self.width/2+100, y_mouth+10, fill=color, outline="")

    def set_face_happy(self, msg="PRET"):
        self.draw_face("#00ffcc", "normal", "happy")
        self.status_label.config(text=msg, fg="#00ffcc")

    def set_face_moving(self, msg="EN ROUTE..."):
        self.draw_face("#ffff00", "normal", "wow")
        self.status_label.config(text=msg, fg="#ffff00")
        self.btn_confirm.pack_forget()

    def set_face_error(self, msg="ERREUR"):
        self.draw_face("#ff4444", "x", "flat")
        self.status_label.config(text=msg, fg="#ff4444")

    async def listen(self, loop):
        self.loop = loop
        while True:
            try:
                async with websockets.connect(f"ws://{SERVER_IP}:{PORT}") as ws:
                    self.ws = ws
                    self.set_face_happy("SYSTÈME CONNECTÉ")
                    async for message in ws:
                        m = message.lower()
                        if "deplacement table" in m:
                            self.set_face_moving(f"LIVRAISON EN COURS")
                        elif "arrived/table" in m:
                            self.set_face_happy("SERVEZ-VOUS !")
                            self.btn_confirm.pack(side="right", padx=20)
                        elif "arrived/bar" in m:
                            self.set_face_happy("DE RETOUR AU BAR")
                            self.btn_confirm.pack_forget()
            except:
                self.ws = None
                self.set_face_error("SERVEUR HORS LIGNE")
                await asyncio.sleep(3)

if __name__ == "__main__":
    root = tk.Tk()
    app = SlayBotVisual(root)
    lp = asyncio.new_event_loop()
    threading.Thread(target=lambda: lp.run_until_complete(app.listen(lp)), daemon=True).start()
    root.mainloop()