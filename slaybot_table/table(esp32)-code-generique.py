import network
import time
from machine import Pin
from umqtt.robust import MQTTClient 
import usocket as socket
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

# Initialisation des composants
led_vert = Pin(PIN_LED_VERT, Pin.OUT)
led_jaune = Pin(PIN_LED_JAUNE, Pin.OUT)
bouton = Pin(PIN_BOUTON, Pin.IN, Pin.PULL_UP)

# Variables d'état
commande_en_cours = False
periode_reset = False
ms_fin_mission = 0

def set_led_state(vert_on):
    """Alterne entre la LED Verte et la LED Jaune."""
    if vert_on:
        led_vert.value(1)
        led_jaune.value(0)
    else:
        led_vert.value(0)
        led_jaune.value(1)

def leds_off():
    """Éteint toutes les LEDs."""
    led_vert.value(0)
    led_jaune.value(0)

async def connect_wifi():
    """Gère la connexion au WiFi Slaybot."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connexion au WiFi...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            await asyncio.sleep(0.5)
    print('WiFi connecté:', wlan.ifconfig())

async def listen_websocket(ws):
    """Écoute les messages du serveur (équivalent on_message_received)."""
    global commande_en_cours, periode_reset, ms_fin_mission
    
    while True:
        try:
            msg = await ws.recv()
            print("Reçu du serveur:", msg)
            
            if "arrived/bar" in msg and commande_en_cours:
                commande_en_cours = False
                periode_reset = True
                ms_fin_mission = time.ticks_ms()
                set_led_state(False) # Reste en jaune pendant le cooldown
                print("Robot au bar, début du cooldown")
        except:
            break
        await asyncio.sleep(0.1)

async def main():
    global commande_en_cours, periode_reset, ms_fin_mission
    
    leds_off()
    await connect_wifi()
    
    # Importation locale pour éviter les erreurs si la lib est absente
    from micro_websockets import client # Exemple de lib websocket client
    
    try:
        async with client.connect(WS_URL) as ws:
            print("Connecté au serveur Slaybot")
            set_led_state(True) # Table prête
            
            # Lance l'écouteur de messages en arrière-plan
            asyncio.create_task(listen_websocket(ws))
            
            while True:
                # Gestion du reset des 20 secondes
                if periode_reset:
                    if time.ticks_diff(time.ticks_ms(), ms_fin_mission) >= DELAI_RESET:
                        periode_reset = False
                        set_led_state(True)
                        print("Reset terminé, table disponible")

                # Gestion du bouton (LOW = pressé avec PULL_UP)
                if bouton.value() == 0 and not commande_en_cours and not periode_reset:
                    print("Envoi de la commande...")
                    await ws.send("order/table/" + TABLE_ID)
                    commande_en_cours = True
                    set_led_state(False) # Passage au jaune
                    await asyncio.sleep(1) # Anti-rebond simple
                
                await asyncio.sleep(0.05)
                
    except Exception as e:
        print("Erreur WebSocket:", e)
        leds_off()
        await asyncio.sleep(5)
        # Redémarrage automatique en cas d'erreur
        import machine
        machine.reset()

# Lancement du programme
try:
    asyncio.run(main())
except KeyboardInterrupt:
    leds_off()