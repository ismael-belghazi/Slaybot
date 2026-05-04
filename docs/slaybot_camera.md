# slaybot_camera

Le module `slaybot_camera` implémente le système de vision par ordinateur pour le suivi de ligne du robot SlayBot, utilisant OpenCV et un contrôleur PID pour maintenir la trajectoire.

## Objectif

Fournir une navigation autonome basée vision :
- Détection ligne noire sur sol blanc.
- Calcul angle correction trajectoire.
- Transmission temps réel angle au hotspot.
- Contrôle PID pour stabilité mouvement.

## Composants

- `main.py` : Code vision avec OpenCV, PID, WebSocket.
- `templates/index.html` : Interface web visualisation.
- `install-camera.sh` : Installation dépendances caméra.

## Classes et fonctions principales

### SlayBotVision
Classe principale :
- `__init__()` : Initialisation caméra, WebSocket, PID.
- `_vision_engine()` : Boucle traitement images.
- `is_valid_line(contour)` : Validation contour ligne.
- `calculate_angle(contour)` : Calcul angle correction.
- `update_pid(error)` : Mise à jour contrôleur PID.
- `send_angle(angle)` : Transmission WebSocket.
- `shutdown()` : Arrêt propre.

### Paramètres PID
- `Kp, Ki, Kd` : Coefficients PID (défaut 0.5, 0.0, 0.1).
- `setpoint` : Angle cible (0°).
- `output_limits` : Limites sortie (-90°, 90°).

## Algorithme vision

### Traitement image
1. Capture frame caméra.
2. Conversion HSV, seuillage noir.
3. Détection contours (findContours).
4. Filtrage contours valides (aire, aspect ratio).
5. Calcul centre ligne, angle correction.

### Contrôle PID
- **Erreur** : Différence angle actuel vs cible.
- **Sortie** : Angle correction appliqué mouvement.
- **Intégrale** : Accumulation erreurs passées.
- **Dérivée** : Vitesse changement erreur.

## Communication WebSocket

### Messages sortants
- `angle/{angle}` : Angle correction en degrés.

### Messages entrants
- `start_vision` : Démarrage traitement.
- `stop_vision` : Arrêt traitement.
- `emergency_stop` : Arrêt immédiat.

## Exemples d'utilisation

### Lancement
```bash
python main.py
```
- Démarre serveur web :8766, WebSocket :8765.

### Visualisation
- Ouvrir http://localhost:8766 pour voir flux caméra.

### Intégration
- Hotspot envoie `start_vision` début mission.
- Robot reçoit `angle/X` pour ajustements.

## Architecture technique

- **OpenCV** : Traitement images, contours.
- **Flask** : Serveur web visualisation.
- **WebSocket** : Communication temps réel.
- **PID** : Contrôle proportionnel-intégral-dérivé.
- **Threading** : Séparation vision et réseau.

## Installation et configuration

### Prérequis
- Caméra USB compatible OpenCV.
- Raspberry Pi ou PC avec caméra.

### Installation
```bash
chmod +x install-camera.sh
./install-camera.sh
```

### Configuration
- Ajuster `CAMERA_INDEX` si multiple caméras.
- Calibrer PID selon environnement.

## API du module

::: slaybot_camera.main

## Dépannage

- **Ligne non détectée** : Ajuster seuillage HSV, éclairage.
- **Angle instable** : Régler coefficients PID.
- **Connexion perdue** : Vérifier réseau, redémarrage auto.
- **Performance lente** : Réduire résolution caméra.