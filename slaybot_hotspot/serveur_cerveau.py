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
            print("[PROCESS ERROR]", e)
            return -1, "", str(e)

# ---------------- COMMANDES ROBOT ----------------
async def move_robot(target_type, target_id=None):
    """ Centralise les appels vers pilote.py et gère l'enchaînement """
    if target_type == "table":
        print(f"[ROBOT] En route vers Table {target_id}")
        await broadcast(f"statut: deplacement table {target_id}")
        code, out, err = await run_process("python3", PILOTE_PATH, "table", str(target_id))
        msg_suffix = f"table/{target_id}"
    else:
        print("[ROBOT] Retour au BAR")
        await broadcast("statut: deplacement bar")
        code, out, err = await run_process("python3", PILOTE_PATH, "bar")
        msg_suffix = "bar"

    if code == 0:
        print(f"[OK] Arrivé : {msg_suffix}")
        await broadcast(f"arrived/{msg_suffix}")
    else:
        print(f"[ERROR] {err}")
        await broadcast(f"error/{msg_suffix}")

# ---------------- EMERGENCY STOP ----------------
async def emergency_stop():
    global process_en_cours
    print("[EMERGENCY] STOP !")
    if process_en_cours and process_en_cours.returncode is None:
        process_en_cours.terminate()
        process_en_cours = None
    
    await broadcast("emergency_stop")
    await broadcast("arrived/bar") # Reset l'état UI

# ---------------- HANDLER ----------------
async def handler(websocket):
    clients_actifs.add(websocket)
    try:
        async for message in websocket:
            msg = message.strip().lower()
            print("[RX]", msg)

            # 1. DÉPLACEMENTS (Ordres de l'APK ou Auto)
            if msg.startswith("go/table/"):
                table_id = msg.split("/")[-1]
                asyncio.create_task(move_robot("table", table_id))

            elif msg == "go/bar":
                asyncio.create_task(move_robot("bar"))

            elif msg == "emergency_stop":
                await emergency_stop()

            # 2. LOGIQUE AUTOMATIQUE (Ton log status/received)
            elif msg == "status/received":
                print("[LOGIC] Client servi, retour bar automatique...")
                # On attend 2 secondes pour que le client s'écarte, puis retour bar
                await asyncio.sleep(2)
                asyncio.create_task(move_robot("bar"))

            # 3. SYNCHRONISATION & RELAIS
            elif msg.startswith("order/table/") or msg.startswith("clean/table/"):
                # Relais vers les APK (Site -> APK ou APK -> APK)
                await broadcast(msg)

            elif any(x in msg for x in ["ready/", "paid/", "cancel/", "status/"]):
                # Autres infos de statut (on relaie à tout le monde)
                await broadcast(msg)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients_actifs.discard(websocket)

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
    print("--------------------------------")
    print(f"SLAYBOT SERVER ONLINE | ws://{ip}:{PORT}")
    print("--------------------------------")
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())