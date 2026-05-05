# slaybot_camera

Ce module implémente le système de vision par ordinateur du robot SlayBot, utilisant OpenCV pour la détection de lignes colorées et le calcul d'angle de direction. Il fournit un flux vidéo en temps réel via une interface web Flask et communique les données de pilotage au serveur hotspot via WebSocket.

## Objectif

Permettre au robot de suivre automatiquement des lignes colorées (jaune, bleu, rouge) sur le sol pour naviguer dans le restaurant, en ajustant l'angle de direction via un contrôleur PID. Fournir une visualisation en temps réel du flux caméra pour le débogage.

## Fichiers principaux

- `main.py` : Logique principale de vision, traitement d'image, serveur Flask et client WebSocket.
- `templates/index.html` : Interface web pour visualisation du flux vidéo avec thème cyberpunk.
- `install-camera.sh` : Script d'installation des dépendances caméra sur Raspberry Pi.

## Fonctionnalités principales

- **Détection de lignes colorées** : Utilise HSV pour identifier jaune, bleu, rouge dans une ROI resserrée.
- **Filtrage intelligent** : Rejette les contours trop petits/gros ou de forme incorrecte pour éviter les meubles.
- **Contrôleur PID** : Calcule l'angle de direction basé sur l'erreur de position de la ligne.
- **Flux vidéo MJPEG** : Serveur Flask pour diffusion en temps réel.
- **Communication WebSocket** : Envoi continu des données (angle, couleur) au pilote.
- **Gestion de perte de ligne** : Maintient l'angle ou freine progressivement si ligne perdue.

## Classes et fonctions importantes

### SlayBotVision
Classe principale de traitement visuel :
- `__init__(camera_index)` : Initialise la caméra et lance le thread de vision.
- `_vision_engine()` : Boucle principale de capture et traitement d'image.
- `_init_cam()` : Configuration caméra V4L2 (résolution 320x240, MJPG).
- `is_valid_line(contour, roi_w, roi_h)` : Filtre les contours valides (surface, forme, solidité).
- `get_stream()` : Générateur pour flux MJPEG.

### Fonctions utilitaires
- `_cleanup_v4l2()` : Libère la caméra avant initialisation.
- `websocket_client(bot_v)` : Envoi asynchrone des données de pilotage.

## Algorithme de suivi de ligne

1. **Capture** : Image brute de la caméra.
2. **ROI** : Découpage à 60-95% de hauteur pour éviter les bords lointains.
3. **Filtrage** : Gaussian blur, conversion HSV, seuillage couleur.
4. **Nettoyage** : Morphologie pour supprimer reflets et bruit.
5. **Détection** : Contours externes, filtrage intelligent.
6. **Suivi** : Fenêtrage glissant pour calculer la trajectoire.
7. **PID** : Calcul angle basé sur erreur (position cible vs centre).
8. **Transmission** : Envoi angle et couleur via WebSocket.

## Exemples d'utilisation

### Visualisation
- Accès à `http://robot_ip:5001/` pour voir le flux avec overlay de trajectoire.
- Couleur détectée affichée en temps réel.

### Intégration
- Lance `python main.py` sur le Raspberry Pi.
- Le WebSocket envoie `{"angle": 15, "color": "JAUNE"}` toutes les 20ms.
- Le pilote utilise l'angle pour ajuster la direction.

## Architecture technique

- **Traitement** : OpenCV avec numpy pour calculs vectoriels.
- **Threading** : Vision en thread séparé pour performance.
- **Web** : Flask pour serveur HTTP, asyncio pour WebSocket.
- **Caméra** : Support V4L2, configuration optimisée pour latence faible.
- **PID** : Paramètres ajustables (KP=0.32, KI=0.002, KD=0.22).

## Installation

Exécutez `install-camera.sh` sur le Raspberry Pi pour installer OpenCV et dépendances.

## Configuration

- IP hotspot : Codée en dur à `10.42.0.1:8765/pilote`.
- Caméra : Index 0 par défaut.
- Résolution : 320x240 pour performance.

## Dépannage

- Si caméra non détectée : Vérifiez `v4l2-ctl --list-devices`.
- Perte de ligne : Ajustez seuils HSV ou paramètres PID.
- Latence : Réduisez résolution ou buffersize.