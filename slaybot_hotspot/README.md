# slaybot_hotspot

Ce module constitue le cerveau central du système SlayBot, gérant le hotspot WiFi, le serveur WebSocket de communication, et l'interface de monitoring. Il orchestre les communications entre l'application mobile, le site web de commande, et le robot physique.

## Objectif

Fournir une infrastructure réseau isolée (hotspot) pour la communication sécurisée entre tous les composants du système, diffuser les événements en temps réel, et piloter les déplacements du robot via des scripts Python.

## Composants

- `serveur_cerveau.py` : Serveur WebSocket asynchrone (asyncio) gérant les connexions et le routage des messages.
- `app.py` : Interface web Flask pour monitoring du système (température CPU, RAM, réseau).
- `templates/index.html` : Dashboard de surveillance avec métriques temps réel.
- `install-hotspot.sh` : Script d'installation automatique du hotspot et dépendances.
- `robot.service` : Service systemd pour démarrage automatique du serveur.
- `requirements.txt` : Dépendances Python (websockets, flask, psutil).

## Fonctionnalités principales

- **Hotspot WiFi** : Création d'un réseau isolé pour communication sécurisée.
- **Serveur WebSocket** : Diffusion d'événements (commandes, nettoyages, paiements) à tous les clients.
- **Pilotage robot** : Exécution de scripts de navigation vers tables ou bar.
- **Monitoring système** : Métriques CPU, RAM, température, statut réseau.
- **Gestion d'urgence** : Arrêt immédiat de tous les processus actifs.
- **Logging** : Traces détaillées des angles de pilotage et événements système.

## Classes et fonctions importantes

### Fonctions globales (serveur_cerveau.py)
- `broadcast_system(message, exclude_path)` : Diffusion de messages à tous les clients connectés.
- `move_robot(target_type, target_id)` : Lance le script de pilotage pour déplacement.
- `emergency_stop()` : Arrêt d'urgence, terminaison processus, remise à zéro.
- `handler(websocket)` : Gestionnaire de connexions WebSocket par endpoint.

### Endpoints WebSocket
- `/` : Connexion générale (APK, site web).
- `/pilote` : Connexion caméra pour données de pilotage (angle, couleur).

### Routes Flask (app.py)
- `/` : Dashboard de monitoring.
- `/stats` : API JSON des métriques système.

## Flux de communication

### Réception d'une commande
1. Site web envoie `order/table/5` via WebSocket.
2. Serveur diffuse à APK et robot.
3. APK valide, envoie `go/table/5`.
4. Serveur lance `python3 pilote.py table 5`.
5. Script pilote utilise données caméra pour navigation.
6. Arrivée : diffusion `arrived/table/5`.

### Pilotage automatique
- Caméra envoie `{"angle": 15, "color": "JAUNE"}` à `/pilote`.
- Stocké dans `/dev/shm/steering_angle` pour accès rapide.
- Script pilote lit l'angle en boucle pour ajustements.

## Exemples d'utilisation

### Connexion APK
```python
import websocket
ws = websocket.WebSocketApp("ws://10.42.0.1:8765")
ws.send("go/table/3")
```

### Monitoring
- Accès à `http://10.42.0.1:5000/` pour dashboard.
- API `/stats` retourne :
```json
{
  "cpu_temp": 45.2,
  "cpu_usage": 23.5,
  "ram_usage": 67.8,
  "inet_ssid": "MyWiFi",
  "inet_signal": "85",
  "ap_status": "Connecté"
}
```

## Architecture technique

- **WebSocket** : Protocole bidirectionnel pour événements temps réel.
- **Asyncio** : Gestion concurrente des connexions et processus.
- **Flask** : Serveur web léger pour interface de monitoring.
- **Systemd** : Démarrage automatique et supervision du service.
- **Shared memory** : Fichier `/dev/shm/steering_angle` pour communication inter-processus.
- **Logging** : Rotation automatique des logs (pilote.log).

## Installation et configuration

### Installation automatique
```bash
chmod +x install-hotspot.sh
./install-hotspot.sh
# Choisir option 0 pour hotspot complet
```

### Configuration réseau
- SSID : `Slaybot`
- Mot de passe : `MHI-Hotspot`
- IP hotspot : `10.42.0.1`
- Sous-réseau : `10.42.0.0/24`
- Port WebSocket : `8765`
- Port web : `5000`

### Démarrage service
```bash
sudo systemctl enable robot.service
sudo systemctl start robot.service
```

## Maintenance

- **Vérifier service** : `sudo systemctl status robot`
- **Logs système** : `journalctl -u robot -f`
- **Logs pilotage** : `tail -f pilote.log`
- **Redémarrer** : `sudo systemctl restart robot`
- **Désactiver hotspot** : Modifier `/etc/hostapd/hostapd.conf` et redémarrer.

## Dépannage

- **Connexion perdue** : Vérifier interfaces `wlan0` (AP) et `wlan1` (internet).
- **Processus bloqué** : Utiliser arrêt d'urgence depuis APK.
- **Température élevée** : Surveiller via dashboard, ventiler si >70°C.
- **Latence réseau** : Vérifier signal WiFi et charge CPU.

