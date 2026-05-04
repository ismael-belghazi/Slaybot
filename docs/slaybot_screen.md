# slaybot_screen

Le module `slaybot_screen` fournit l'interface graphique embarquée du robot SlayBot, offrant une interface utilisateur immersive avec visage animé, effets visuels cyberpunk, et contrôles tactiles.

## Objectif

Afficher l'état du robot de manière visuelle et interactive :
- Visage animé changeant selon l'état (idle, moving, arrived, emergency).
- Boutons tactiles pour confirmation livraison et arrêt d'urgence.
- Pavé numérique pour paramètres administrateur.
- Communication temps réel avec le hotspot.

## Composants

- `face.py` : Application Tkinter avec animations, WebSocket, interface tactile.
- `install-screen.sh` : Installation dépendances sur Raspberry Pi.
- `requirements.txt` : Dépendances (tkinter, websockets, asyncio).

## Classes et fonctions principales

### SlayBotTactical
Classe principale :
- `__init__(root)` : Initialisation fullscreen, canvas, bindings.
- `run_boot()` : Séquence boot animée avec logs système.
- `listen()` : Boucle WebSocket asynchrone.
- `handle_click(event)` : Gestion interactions tactiles.
- `show_numpad()` : Pavé numérique administrateur.
- `update_ui()` : Rendu 60 FPS avec animations.
- `blink_logic()` : Clignotement yeux.

### Fonctions dessin
- `draw_boot_screen(cx, cy)` : Écran démarrage.
- `draw_tactical_hud(cx, cy)` : Viseur, status système.
- `draw_face(cx, cy, color)` : Visage avec yeux, bouche, nœud.
- `draw_tactical_buttons()` : Boutons CMD, KILL_SW.

## États du robot

- **booting** : Séquence démarrage avec progression.
- **idle** : Prêt, yeux ouverts, bouche neutre.
- **moving** : En déplacement, yeux plissés, bouche courbée.
- **arrived** : Arrivée, bouton confirmation affiché.
- **emergency** : Urgence, couleur rouge, yeux fermés.

## Communication WebSocket

### Messages reçus
- `go/table/X` ou `clean/table/X` : Passage moving.
- `statut: deplacement table X` : Confirmation déplacement.
- `arrived/table/X` : Passage arrived.
- `arrived/bar` : Retour idle.
- `emergency_stop` : Passage emergency.

### Messages envoyés
- `STATUS/TACTICAL_CONNECTED` : Confirmation connexion.
- `status/received` : Confirmation livraison.
- `emergency_stop` : Signal urgence.

## Exemples d'utilisation

### Interaction
- **Confirmation** : Toucher bouton vert après arrivée.
- **Urgence** : Bouton rouge en haut droite.
- **Admin** : Bouton CMD bas droite, mot de passe "2403".

### États visuels
- **Connexion perdue** : Couleur rouge, status "LOST".
- **Déplacement** : Yeux animés, bouche dynamique.

## Architecture technique

- **Tkinter** : Interface avec canvas pour animations.
- **Asyncio/WebSocket** : Communication réseau.
- **Threading** : Séparation UI et réseau.
- **Mathématiques** : Calculs trigonométriques pour animations.

## Installation et lancement

### Installation
```bash
chmod +x install-screen.sh
./install-screen.sh
```

### Lancement
```bash
python face.py
```

### Configuration
- IP hotspot : `10.42.0.1:8765` (codé).
- Mot de passe admin : `2403`.
- Version : `v4.1-MHI-INC`.

## API du module

::: slaybot_screen.face

## Dépannage

- **Interface non responsive** : Vérifier connexion WebSocket.
- **Animations saccadées** : Réduire résolution.
- **Touchscreen non détecté** : Calibrer avec xinput-calibrator.
