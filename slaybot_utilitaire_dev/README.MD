# slaybot_utilitaire_dev

Ce module rassemble les outils de développement, simulation et utilitaires pour le projet SlayBot, facilitant les tests logiciels, la génération de QR codes, et la validation des protocoles de communication.

## Objectif

Fournir un environnement de développement complet pour tester les interactions WebSocket, simuler le comportement du robot, générer des codes QR pour l'accès client, et scanner le réseau pour le débogage.

## Fichiers principaux

- `simulation.py` : Simulateur graphique du robot avec serveur WebSocket intégré.
- `generate_qr.py` : Génération de QR codes pour accès test aux tables.
- `scan.py` : Outil de scan réseau pour détecter les appareils connectés.
- `temp.py` : Script temporaire pour génération QR code site web.
- `requirements.txt` : Dépendances Python (PyQt5, qrcode, websockets).
- `.env` / `.env.example` : Fichiers de configuration environnement.

## Fonctionnalités principales

- **Simulation robot** : Interface graphique avec déplacements animés, files d'attente, validation livraisons.
- **Serveur WebSocket** : Reproduction fidèle du protocole serveur pour tests.
- **Génération QR** : Création de codes pour accès client en développement.
- **Scan réseau** : Détection des IPs actives sur le sous-réseau hotspot.
- **Débogage** : Outils pour valider communications et états système.

## Classes et fonctions importantes

### RobotSimulator (simulation.py)
Classe principale du simulateur :
- `__init__()` : Initialisation interface PyQt5, positions tables, chemins.
- `add_task(command)` : Ajout de tâches (go/table/X) à la file.
- `update_robot_logic()` : Logique de déplacement et états.
- `move_step()` : Animation pas à pas vers cible.
- `show_validation_popup()` : Popup de confirmation livraison.
- `paintEvent(event)` : Rendu graphique tables, chemins, robot.

### Fonctions utilitaires
- `broadcast(message)` : Diffusion messages à tous clients connectés.
- `ws_handler(ws, path, sim)` : Gestionnaire WebSocket pour commandes.
- `get_local_ip()` : Détection IP locale pour serveur.
- `start_server(sim)` : Lancement serveur WebSocket.

## Protocoles supportés

### Messages entrants (simulation)
- `go/table/X` : Déplacement vers table X (1-4).
- `emergency_stop` : Arrêt immédiat, vidage file.

### Messages sortants (simulation)
- `arrived/table/X` : Arrivée à table X.
- `arrived/bar` : Retour au bar.
- `validated/X` : Confirmation livraison par utilisateur.

## Exemples d'utilisation

### Simulation robot
```bash
python simulation.py
```
- Interface graphique s'ouvre.
- Envoyer `go/table/1` via WebSocket pour déplacer robot.
- Valider livraison dans popup pour retour au bar.

### Génération QR test
```bash
python generate_qr.py
```
- Génère `qrcodes/table_1_test.png` avec URL locale.
- Utiliser pour tests accès client sans déploiement.

### Scan réseau
```bash
python scan.py
```
- Ping toutes IPs 10.42.0.1-254.
- Affiche appareils actifs sur hotspot.

## Architecture technique

- **PyQt5** : Interface graphique pour simulation.
- **WebSockets** : Communication temps réel.
- **Threading** : Séparation UI et serveur réseau.
- **QTimer** : Animation 30 FPS pour fluidité.
- **QRCode** : Génération codes avec correction d'erreur.
- **Subprocess** : Ping réseau pour scan.

## Installation et configuration

### Dépendances
```bash
pip install -r requirements.txt
```

### Configuration
- Copier `.env.example` vers `.env`.
- Adapter variables selon environnement de test.

## Utilisation en développement

### Tests WebSocket
- Lancer simulation comme serveur de remplacement.
- Tester APK, site web, modules table contre ce serveur.
- Valider séquences : commande → déplacement → arrivée → validation → retour.

### Débogage réseau
- Utiliser `scan.py` pour vérifier connectivité hotspot.
- Générer QR pour tests accès client local.

### Simulation scénarios
- Tester files d'attente multiples.
- Simuler arrêts d'urgence.
- Valider chemins et timings.

## Dépannage

- **Interface ne s'affiche pas** : Vérifier PyQt5 installé, display disponible.
- **WebSocket refuse connexions** : Vérifier port 8765 libre.
- **Déplacements erratiques** : Vérifier définitions TABLES et PATHS.
- **QR non scanné** : Augmenter box_size ou error_correction.

