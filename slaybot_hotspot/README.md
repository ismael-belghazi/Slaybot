
# Slaybot : Système Central (Cerveau & Hotspot)

> Ce dépôt contient l'intelligence centrale du robot. Le système configure automatiquement un Raspberry Pi pour qu'il devienne un point d'accès Wi-Fi privé (Hotspot) et un serveur de communication temps réel via WebSockets.

# Architecture du Réseau
> Le robot fonctionne en circuit fermé (LAN local) pour garantir une latence proche de zéro.

>Cerveau (RPi) : Gère le Wi-Fi "Slaybot" et route les messages JSON.

> Clients : Téléphones (commandes APK) et ESP32 (moteurs) se connectent tous au Cerveau.

# Pré-requis (À faire AVANT l'installation)

### Pour que le script:
install.sh 
### réussisse, assure-toi de respecter ces points :

1. Emplacement des fichiers

> Tous les fichiers doivent être placés dans le dossier suivant :
```bash
mkdir -p /home/admin/Documents/hotspot
```
2. Fichiers nécessaires
> * vérifie que tu as bien ces 3 fichiers dans le dossier :
      - serveur_cerveau.py (Ton code Python principal)
      - robot.service (La configuration du service Systemd)
      - install.sh (Le script d'automatisation)

3. Connexion Internet
> Le Raspberry Pi doit être connecté à Internet (via Ethernet ou Wi-Fi temporaire) uniquement pendant l'installation pour télécharger les dépendances.

# Installation Rapide
Une fois les fichiers copiés sur le Raspberry Pi, lance ces commandes :

```Bash
cd /home/admin/Documents/hotspot
chmod +x install.sh
./install.sh
``` 
### Que fait le script ?
> Met à jour le système Linux.

### Installe NetworkManager pour gérer le Wi-Fi.

- Crée le Hotspot Slaybot (Mot de passe : MHI-Hotspot).

- Crée un environnement virtuel Python (venv) et installe websockets.

- Installe et active le service de démarrage automatique (robot.service).

# Fiche Technique
Paramètre	Valeur
> - SSID Wi-Fi	Slaybot
> - Mot de passe	MHI-Hotspot
> - IP du Cerveau	10.42.0.1
> - Port WebSocket	8765

> URL Client	ws://10.42.0.1:8765 

## Commandes Utiles
### Une fois installé, le serveur se lance tout seul au démarrage. En cas de besoin :

- Voir si le robot tourne :
```bash 
sudo systemctl status robot.service
``` 

- Lire les logs du serveur en direct :
```bash 
journalctl -u robot.service -f
```
- Redémarrer le serveur (après modif du code Python) :
```bash 
sudo systemctl restart robot.service
```
- Vérifier l'état du Wi-Fi :
```bash 
nmcli connection show
```

### Format des Messages (JSON)
- Le cerveau communique via des objets JSON. Exemple pour un mouvement :
```json
{
  "action": "MOVE",
  "direction": "FORWARD",
  "speed": 100
}
```
*Note : Une fois l'installation terminée, le Raspberry Pi n'aura plus accès à Internet (priorité au Hotspot). Pour effectuer une mise à jour, connectez un câble Ethernet.*

SlayBot Project - 2026 ©