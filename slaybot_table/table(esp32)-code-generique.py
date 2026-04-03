import network
import time
from machine import Pin, reset
import uasyncio as asyncio

# --- CONFIGURATION RÉSEAU ---
SSID = "Slaybot"
PASSWORD = "MHI-Hotspot"
WS_URL = "ws://10.42.0.1:8765"

# --- CONFIGURATION MATÉRIELLE ---
TABLE_ID = "1"
PIN_LED_VERT = 18
PIN_LED_JAUNE = 19
PIN_BOUTON = 4

# --- PARAMÈTRES ---
DELAI_RESET = 20000  # 20 secondes en millisecondes

# Initialisation composants
led_vert = Pin(PIN_LED_VERT, Pin.OUT)
led_jaune = Pin(PIN_LED_JAUNE, Pin.OUT)
bouton = Pin(PIN_BOUTON, Pin.IN, Pin.PULL_UP)

# Variables d'état
commande_en_cours = False
periode_reset = False
ms_fin_mission = 0

def set_led_state(vert_on: bool):
    """Active la LED verte si vert_on, sinon la jaune."""
    led_vert.value(1 if vert_on else 0)
    led_jaune.value(0 if vert_on else 1)

def leds_off():
    """Éteint toutes les LEDs."""
    led_vert.value(0)
    led_jaune.value(0)

async def connect_wifi():
    """Connexion au WiFi Slaybot."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connexion au WiFi...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            await asyncio.sleep(0.5)
    print('WiFi connecté:', wlan.ifconfig())

async def listen_websocket(ws):
    """Écoute les messages du serveur."""
    global commande_en_cours, periode_reset, ms_fin_mission
    while True:
        try:
            msg = await ws.recv()
            print("Reçu du serveur:", msg)
            if "arrived/bar" in msg and commande_en_cours:
                commande_en_cours = False
                periode_reset = True
                ms_fin_mission = time.ticks_ms()
                set_led_state(False)  # LED jaune pendant cooldown
                print("Robot revenu au bar, début cooldown")
        except Exception as e:
            print("Erreur écoute WS:", e)
            break
        await asyncio.sleep(0.05)

async def main():
    global commande_en_cours, periode_reset, ms_fin_mission
    
    leds_off()
    await connect_wifi()
    
    from micro_websockets import client  # Lib WebSocket adaptée ESP32
    
    while True:
        try:
            async with client.connect(WS_URL) as ws:
                print("Connecté au serveur Slaybot")
                set_led_state(True)  # Table dispo

                # Lancement écoute WS en tâche de fond
                asyncio.create_task(listen_websocket(ws))

                while True:
                    # Gestion du cooldown
                    if periode_reset:
                        if time.ticks_diff(time.ticks_ms(), ms_fin_mission) >= DELAI_RESET:
                            periode_reset = False
                            set_led_state(True)
                            print("Cooldown terminé, table dispo")

                    # Gestion du bouton (LOW = pressé avec PULL_UP)
                    if bouton.value() == 0 and not commande_en_cours and not periode_reset:
                        print("Envoi commande CLEAN...")
                        await ws.send("clean/table/" + TABLE_ID)
                        commande_en_cours = True
                        set_led_state(False)  # LED jaune
                        await asyncio.sleep(0.5)  # Anti-rebond

                    await asyncio.sleep(0.05)

        except Exception as e:
            print("Erreur WebSocket:", e)
            leds_off()
            await asyncio.sleep(5)
            print("Tentative reconnexion...")
            reset()  # Redémarrage automatique

# Lancement du programme
try:
    asyncio.run(main())
except KeyboardInterrupt:
    leds_off()