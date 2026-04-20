import asyncio
import websockets
import socket
import os

# ---------------- CONFIG ----------------
HOST = "0.0.0.0"
PORT = 8765

BASE_DIR = "/home/hotspot/Documents/slaybot_hotspot"
PILOTE_PATH = os.path.join(BASE_DIR, "pilote.py")

clients_actifs = set()
process_en_cours = None 
lock = asyncio.Lock()  # Sécurité anti-conflit moteurs

# ---------------- BROADCAST ----------------
async def broadcast(message):
    if clients_actifs:
        print(f"[BROADCAST] {message}")
        # On utilise asyncio.gather pour envoyer à tout le monde en parallèle
        await asyncio.gather(*(c.send(message) for c in clients_actifs), return_exceptions=True)

# ---------------- GESTION PROCESS ----------------
async def run_process(*args):
    global process_en_cours
    async with lock:
        try:
            process_en_cours = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process_en_cours.communicate()
            code = process_en_cours.returncode
            process_en_cours = None
            return code, stdout.decode(), stderr.decode()
        except Exception as e:
            process_en_cours = None
            print(f"[PROCESS ERROR] {e}")
            return -1, "", str(e)

# ---------------- COMMANDES ROBOT ----------------
async def move_robot(target_type, target_id=None):
    """ Centralise les appels vers pilote.py et gère l'enchaînement """
    if target_type == "table":
        print(f"[ROBOT] En route vers Table {target_id}")
        # CORRECTION : On envoie exactement ce que l'UI Tkinter attend
        await broadcast(f"order/table/{target_id}") 
        code, out, err = await run_process("python3", PILOTE_PATH, "table", str(target_id))
        msg_suffix = f"table/{target_id}"
    else:
        print("[ROBOT] Retour au BAR")
        await broadcast("go/bar")
        code, out, err = await run_process("python3", PILOTE_PATH, "bar")
        msg_suffix = "bar"

    if code == 0:
        print(f"[OK] Arrivé : {msg_suffix}")
        await broadcast(f"arrived/{msg_suffix}")
    else:
        print(f"[ERROR] {err}")
        # En cas d'erreur physique, on avertit l'UI
        await broadcast(f"status/emergency_stop")

# ---------------- EMERGENCY STOP ----------------
async def emergency_stop():
    global process_en_cours
    print("[EMERGENCY] STOP !")
    if process_en_cours and process_en_cours.returncode is None:
        try:
            process_en_cours.terminate()
        except:
            pass
        process_en_cours = None
    
    # On envoie le signal d'arrêt à toutes les interfaces
    await broadcast("status/emergency_stop")

# ---------------- HANDLER ----------------
async def handler(websocket):
    clients_actifs.add(websocket)
    print(f"[CONNEXION] Nouveau client. Total : {len(clients_actifs)}")
    try:
        async for message in websocket:
            msg = message.strip().lower()
            print(f"[RX] {msg}")

            # 1. DÉPLACEMENTS (Ordres de l'APK ou Auto)
            if msg.startswith("go/table/"):
                table_id = msg.split("/")[-1]
                asyncio.create_task(move_robot("table", table_id))

            elif msg == "go/bar":
                asyncio.create_task(move_robot("bar"))

            elif msg == "status/emergency_stop": # Match avec l'envoi de l'UI
                await emergency_stop()

            # 2. LOGIQUE DE CONFIRMATION (Bouton vert sur le Robot)
            elif msg == "status/received":
                print("[LOGIC] Client a cliqué sur confirmer, retour bar...")
                # On informe tout le monde que c'est reçu
                await broadcast("status/received")
                await asyncio.sleep(2)
                asyncio.create_task(move_robot("bar"))

            # 3. SYNCHRONISATION & RELAIS (Site Web / APK)
            elif msg.startswith("order/table/") or msg.startswith("clean/table/"):
                await broadcast(msg)

            elif any(x in msg for x in ["ready/", "paid/", "cancel/", "status/"]):
                await broadcast(msg)

            elif msg == "arrived/table": # Si le pilote simule l'arrivée
                 await broadcast("arrived/table")

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients_actifs.discard(websocket)
        print(f"[DECONNEXION] Client parti. Reste : {len(clients_actifs)}")

# ---------------- IP & MAIN ----------------
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except: return "127.0.0.1"
    finally: s.close()

async def main():
    ip = get_local_ip()
    print("========================================")
    print(f"  SLAYBOT SERVER : ONLINE")
    print(f"  ADRESSE : ws://{ip}:{PORT}")
    print("========================================")
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future() # Maintient le serveur ouvert

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[STOP] Serveur arrêté manuellement.")