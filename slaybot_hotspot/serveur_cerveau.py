import asyncio
import websockets
import subprocess

# --- CONFIGURATION ---
HOST = "0.0.0.0"
PORT = 8765

clients_actifs = set()

async def piloter_deplacement(table_id):
    """Lance le script pilote pour la table et notifie l'APK à la fin."""
    print(f"Déplacement du robot vers la Table {table_id}")
    try:
        process = await asyncio.create_subprocess_exec(
            'python3', 'pilote.py', table_id,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            print(f"Robot revenu à la base (Bar).")
            await broadcast("arrived/bar")
        else:
            print(f"Erreur pilote : {stderr.decode()}")
    except Exception as e:
        print(f"Erreur critique pilote : {e}")

async def broadcast(message):
    """Envoie le message à tous les clients connectés."""
    if clients_actifs:
        print(f"Broadcast : {message}")
        await asyncio.gather(*[client.send(message) for client in clients_actifs])

async def handler(websocket):
    """Gestion des messages reçus des clients."""
    clients_actifs.add(websocket)
    try:
        async for message in websocket:
            msg = message.strip().lower()
            print(f"Reçu : {msg}")

            # --- Commande déplacement depuis APK ---
            if msg.startswith("go/"):
                table_id = msg.split("/")[-1]
                asyncio.create_task(piloter_deplacement(table_id))
                await broadcast(f"statut: deplacement table {table_id}")

            # --- Nettoyage depuis ESP32 ---
            elif msg.startswith("clean/table/"):
                table_id = msg.split("/")[-1]
                await broadcast(f"CLEAN Table {table_id}")
                print(f"Nettoyage demandé Table {table_id}")

            # --- Commande cuisine depuis APK ou Web ---
            elif msg.startswith("order/table/"):
                table_id = msg.split("/")[-1]
                await broadcast(f"ORD Table {table_id}")
                print(f"Commande reçue Table {table_id}")

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
        await asyncio.Future()  # maintien serveur en vie

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServeur arrêté manuellement.")