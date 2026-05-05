# slaybot_screen

Le module `slaybot_screen` fournit l'interface graphique embarquée du robot SlayBot, offrant une interface utilisateur immersive avec un visage animé, des effets visuels cyberpunk, et des contrôles tactiles pour la gestion des états du robot.

## Objectif

Afficher l'état du robot de manière visuelle et interactive, permettre la confirmation de livraison, gérer les arrêts d'urgence, et fournir un pavé numérique pour les paramètres administrateur.

## Fichiers principaux

- `face.py` : Application principale Tkinter avec animations et WebSocket.
- `install-screen.sh` : Script d'installation des dépendances sur Raspberry Pi.
- `requirements.txt` : Dépendances Python (tkinter, websockets, asyncio).

## Fonctionnalités principales

- **Visage animé** : Expressions faciales changeant selon l'état (idle, moving, arrived, emergency).
- **Effets visuels** : Scanlines CRT, radar animé, clignotement des yeux.
- **Boutons tactiles** : Confirmation livraison, arrêt d'urgence, accès paramètres.
- **Pavé numérique** : Interface d'administration pour extinction système.
- **Connexion WebSocket** : Communication temps réel avec le hotspot.
- **Mode plein écran** : Interface immersive sans bordures.

## Classes et fonctions importantes

### SlayBotTactical
Classe principale de l'application :
- `__init__(root)` : Initialisation fullscreen, canvas, bindings.
- `run_boot()` : Séquence de boot animée avec logs système.
- `listen()` : Boucle WebSocket asynchrone pour réception messages.
- `start_network()` : Lancement du thread réseau.
- `handle_click(event)` : Gestion des interactions tactiles.
- `show_numpad()` : Affichage du pavé numérique administrateur.
- `update_ui()` : Boucle de rendu graphique (60 FPS).
- `blink_logic()` : Animation de clignotement des yeux.

### Fonctions de dessin
- `draw_boot_screen(cx, cy)` : Écran de démarrage avec barre de progression.
- `draw_tactical_hud(cx, cy)` : Viseur de ciblage et status système.
- `draw_face(cx, cy, color)` : Visage avec yeux, bouche, nœud papillon.
- `draw_tactical_buttons()` : Boutons CMD et KILL_SW.

## États du robot

- **booting** : Séquence de démarrage avec logs et progression.
- **idle** : État prêt, yeux ouverts, bouche neutre.
- **moving** : Yeux plissés, bouche courbée, mouvement vers table.
- **arrived** : Bouton de confirmation affiché, bouche souriante.
- **emergency** : Couleur rouge, yeux fermés, bouche froncée.

## Communication WebSocket

### Messages reçus
- `go/table/X` ou `clean/table/X` : Passage en état `moving`.
- `statut: deplacement table X` : Confirmation déplacement.
- `arrived/table/X` : Passage en état `arrived`.
- `arrived/bar` : Retour en état `idle`.
- `emergency_stop` : Passage en état `emergency`.

### Messages envoyés
- `STATUS/TACTICAL_CONNECTED` : Confirmation connexion.
- `status/received` : Confirmation livraison par utilisateur.
- `emergency_stop` : Signal d'arrêt d'urgence.

## Exemples d'utilisation

### Interaction utilisateur
- **Confirmation livraison** : Toucher le bouton vert "CONFIRM SYSTEM" après arrivée.
- **Arrêt d'urgence** : Toucher le bouton rouge "KILL_SW" en haut à droite.
- **Accès admin** : Toucher le bouton "CMD" en bas à droite, entrer mot de passe "2403".

### États visuels
- **Connexion perdue** : Couleur rouge, status "CORE_LINK: LOST".
- **Déplacement** : Yeux animés, bouche dynamique.
- **Arrivée** : Bouton interactif affiché sur la bouche.

## Architecture technique

- **Tkinter** : Interface graphique avec canvas pour animations.
- **Asyncio/WebSocket** : Communication réseau non-bloquante.
- **Threading** : Séparation UI et réseau pour fluidité.
- **Mathématiques** : Calculs trigonométriques pour animations (balayage regard, courbes bouche).
- **Fullscreen** : Configuration Raspberry Pi pour kiosk mode.

## Installation et lancement

### Installation
```bash
chmod +x install-screen.sh
./install-screen.sh
```

### Lancement manuel
```bash
python face.py
```

### Configuration
- IP hotspot : `10.42.0.1:8765` (codé en dur).
- Mot de passe admin : `2403`.
- Version : `v4.1-MHI-INC`.

## Dépannage

- **Interface non responsive** : Vérifier connexion WebSocket.
- **Animations saccadées** : Réduire résolution ou optimiser calculs.
- **Touchscreen non détecté** : Calibrer avec `xinput-calibrator`.
- **Boot loop** : Vérifier logs console pour erreurs réseau.

## Notes

- Vérifier la variable `SERVER_IP` si le hotspot change d’adresse.
- Le module doit pouvoir accéder au hotspot local pour rester connecté.

