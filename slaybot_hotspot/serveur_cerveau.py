import asyncio
import websockets
import socket
import os
import json
import logging

# ---------------- CONFIG ----------------
HOST = "0.0.0.0"
PORT = 8765
BASE_DIR = "/home/hotspot/Documents/slaybot_hotspot"
PILOTE_PATH = os.path.join(BASE_DIR, "pilote.py")
ANGLE_FILE = "/dev/shm/steering_angle"

# --- CONFIGURATION DES LOGS ---
# Console 1 (Standard) : Commandes et APK
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger("MAIN")

# Console 2 (Pilote) : Uniquement pour la vision et l'angle
pilote_logger = logging.getLogger("PILOTE")
fh = logging.FileHandler('pilote_debug.log')
pilote_logger.addHandler(fh)

clients_actifs = set()
process_en_cours = None 
lock = asyncio.Lock()

# Initialisation
with open(ANGLE_FILE, "w") as f: f.write("0")

# ---------------- BROADCAST (APK UNIQUEMENT) ----------------
async def broadcast_apk(message):
    """ Envoie uniquement aux interfaces (APK/Web), pas aux caméras """
    if clients_actifs:
        # On filtre pour ne pas envoyer aux connexions /pilote
        targets = [c for c in clients_actifs if getattr(c, 'path', '') != "/pilote"]
        if targets:
            await asyncio.gather(*(t.send(message) for t in targets), return_exceptions=True)

# ---------------- GESTION PROCESS ----------------
async def run_process(*args):
    global process_en_cours
    async with lock:
        try:
            process_en_cours = await asyncio.create_subprocess_exec(
                *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process_en_cours.communicate()
            code = process_en_cours.returncode
            process_en_cours = None
            return code, stdout.decode(), stderr.decode()
        except Exception as e:
            process_en_cours = None
            logger.error(f"Erreur Process: {e}")
            return -1, "", str(e)

# ---------------- COMMANDES ROBOT ----------------
async def move_robot(target_type, target_id=None):
    if target_type == "table":
        logger.info(f"ORDRE : Direction Table {target_id}")
        await broadcast_apk(f"statut: deplacement table {target_id}")
        code, out, err = await run_process("python3", PILOTE_PATH, "table", str(target_id))
        msg_suffix = f"table/{target_id}"
    else:
        logger.info("ORDRE : Retour BAR")
        await broadcast_apk("statut: deplacement bar")
        code, out, err = await run_process("python3", PILOTE_PATH, "bar")
        msg_suffix = "bar"

    if code == 0:
        logger.info(f"ARRIVÉ : {msg_suffix}")
        await broadcast_apk(f"arrived/{msg_suffix}")
    else:
        logger.error(f"ÉCHEC : {err}")
        await broadcast_apk(f"error/{msg_suffix}")

# ---------------- EMERGENCY STOP ----------------
async def emergency_stop():
    global process_en_cours
    logger.warning("!!! EMERGENCY STOP !!!")
    if process_en_cours and process_en_cours.returncode is None:
        process_en_cours.terminate()
        process_en_cours = None
    
    with open(ANGLE_FILE, "w") as f: f.write("0")
    await broadcast_apk("emergency_stop")
    await broadcast_apk("arrived/bar")

# ---------------- HANDLER ----------------
async def handler(websocket, path):
    # On attache le chemin au websocket pour le filtrage
    websocket.path = path
    clients_actifs.add(websocket)
    
    try:
        async for message in websocket:
            # --- FLUX CAMÉRA (LOGS SÉPARÉS) ---
            if path == "/pilote":
                try:
                    data = json.loads(message)
                    angle = data.get("angle", 0)
                    color = data.get("color", "NONE")
                    
                    # On écrit en RAM
                    with open(ANGLE_FILE, "w") as f: f.write(str(angle))

                    # Log spécifique "Pilote" (optionnel : commente la ligne suivante si c est ilisible)
                    pilote_logger.info(f"Angle: {angle} | Couleur: {color}")
                except: pass

            # --- COMMANDES APK (LOGS PRINCIPAUX) ---
            else:
                msg = message.strip().lower()
                logger.info(f"APK RX: {msg}")

                if msg.startswith("go/table/"):
                    asyncio.create_task(move_robot("table", msg.split("/")[-1]))

                elif msg == "go/bar":
                    asyncio.create_task(move_robot("bar"))

                elif msg == "emergency_stop":
                    await emergency_stop()

                elif msg == "status/received":
                    await asyncio.sleep(2)
                    asyncio.create_task(move_robot("bar"))

                elif any(x in msg for x in ["order/", "clean/", "ready/", "paid/", "status/"]):
                    await broadcast_apk(msg)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients_actifs.discard(websocket)

# ---------------- MAIN ----------------
async def main():
    ip = socket.gethostbyname(socket.gethostname())
    print(f"\n" + "="*40)
    print(f"  MAIN CONSOLE : Commandes & APK")
    print(f"  PILOTE LOGS  : Enregistrés dans pilote_debug.log")
    print(f"  SERVER       : ws://0.0.0.0:{PORT}")
    print("="*40 + "\n")
    
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())