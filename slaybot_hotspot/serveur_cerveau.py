import asyncio
import websockets
import json
import subprocess

# --- CONFIGURATION ---
# "0.0.0.0" permet d'écouter sur toutes les interfaces (Ethernet, Wi-Fi Hotspot)
HOST = "0.0.0.0" 
PORT = 8765

TABLE_COLORS = {
    "1": "ROUGE",
    "2": "VERT",
    "3": "BLEU",
    "4": "JAUNE"
}

clients_actifs = set()

async def piloter_deplacement(table_id):
    """ 
    Lance le script de mouvement en lui passant la table en argument.
    Attend que le script se termine avant de signaler le retour au bar.
    """
    print(f"Lancement du script de pilotage pour la Table {table_id}")
    
    try:
        # On lance : python3 pilote.py [ID_TABLE]
        process = await asyncio.create_subprocess_exec(
            'python3', 'pilote.py', table_id,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # On attend la fin du script (le robot a fini son trajet aller-retour)
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            print(f"Le robot est revenu à sa base (Bar).")
            # On prévient l'APK Kivy que le robot est disponible
            await broadcast("arrived/bar")
        else:
            print(f"Erreur dans le script pilote : {stderr.decode()}")

    except Exception as e:
        print(f"Erreur critique lors du lancement du pilote : {e}")

async def broadcast(message):
    """ Envoie un message à tous les appareils connectés (APK, ESP32, etc). """
    if clients_actifs:
        print(f"Broadcast : {message}")
        await asyncio.gather(*[client.send(message) for client in clients_actifs])

async def handler(websocket):
    """ Gère la réception des messages de tous les clients. """
    clients_actifs.add(websocket)
    try:
        async for message in websocket:
            msg = message.strip().lower()
            print(f"Reçu : {msg}")

            # --- CAS 1 : COMMANDE DE MOUVEMENT (Depuis l'APK) ---
            if msg.startswith("go/"):
                table_id = msg.split("/")[-1]
                # On lance le mouvement en tâche de fond pour ne pas bloquer le serveur
                asyncio.create_task(piloter_deplacement(table_id))
                await broadcast(f"statut: deplacement table {table_id}")

            # --- CAS 2 : DEMANDE DE COMMANDE (Depuis ESP32 ou Bouton) ---
            elif msg.startswith("order/table/"):
                # On retransmet simplement l'info à l'APK pour l'afficher en CUISINE
                await broadcast(msg)
                table_id = msg.split("/")[-1]
                print(f"Commande demandée par la table {table_id}")

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"Erreur handler : {e}")
    finally:
        clients_actifs.remove(websocket)

async def main():
    print("-------------------------------------------")
    print(f"SERVEUR SLAYBOT EN LIGNE")
    print(f"IP : {HOST} | Port : {PORT}")
    print("-------------------------------------------")
    
    async with websockets.serve(handler, HOST, PORT):
        # Maintient le serveur en vie indéfiniment
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Serveur arrêté manuellement.")