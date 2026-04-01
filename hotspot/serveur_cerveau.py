import asyncio
import websockets
import json
import asyncio
import subprocess

# --- CONFIGURATION ---
HOST = "0.0.0.0" #Adresse IP du serveur (Hotspot du Raspberry Pi 10.42.0.1)
PORT = 8765

TABLE_COLORS = {
    "1": "ROUGE",
    "2": "VERT",
    "3": "BLEU",
    "4": "JAUNE"
}

clients_actifs = set()

async def piloter_deplacement(table_id):
    """ Lance le script de mouvement en lui passant la table en argument. """
    print(f"Lancement du script de pilotage pour la Table {table_id}")
    
    try:
        # On lance : python3 pilote.py [ID_TABLE]
        # On utilise 'run' pour attendre que le script se termine
        process = await asyncio.create_subprocess_exec(
            'python3', 'pilote.py', table_id,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # On attend la fin du script (le robot est arrivé)
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            print(f"Le script pilote a terminé avec succès.")
            # On prévient l'APK que la mission est finie
            await broadcast("arrived/bar")
        else:
            print(f"Erreur dans le script pilote : {stderr.decode()}")

    except Exception as e:
        print(f"Impossible de lancer le script pilote : {e}")

async def broadcast(message):
    """ Envoie un message à tous les appareils connectés. """
    if clients_actifs:
        await asyncio.gather(*[client.send(message) for client in clients_actifs])

async def handler(websocket):
    clients_actifs.add(websocket)
    try:
        async for message in websocket:
            msg = message.strip().lower()
            print(f"Commande reçue : {msg}")

            if msg.startswith("go/"):
                table_id = msg.split("/")[-1]
                asyncio.create_task(piloter_deplacement(table_id))
            
            await broadcast(f"STATUT: Déplacement vers table {msg.split('/')[-1]}")

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients_actifs.remove(websocket)

async def main():
    print(f"Serveur Slaybot en ligne (IP: {HOST})")
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())