# slaybot_utilitaire_dev

Le module `slaybot_utilitaire_dev` rassemble les outils de développement, simulation et utilitaires pour faciliter les tests logiciels, la génération de QR codes, et la validation des protocoles de communication.

## Objectif

Fournir un environnement de développement complet :
- Simulation graphique du robot avec déplacements.
- Serveur WebSocket pour tests protocoles.
- Génération QR codes pour accès client.
- Scan réseau pour débogage connexions.
- Outils temporaires pour développement.

## Composants

- `simulation.py` : Simulateur PyQt5 avec serveur WebSocket.
- `generate_qr.py` : Génération QR codes test.
- `scan.py` : Scan réseau IPs actives.
- `temp.py` : Script génération QR site web.
- `requirements.txt` : Dépendances (PyQt5, qrcode, websockets).
- `.env` / `.env.example` : Configuration environnement.

## Classes et fonctions principales

### RobotSimulator (simulation.py)
Classe simulateur :
- `__init__()` : Interface PyQt5, positions tables, chemins.
- `add_task(command)` : Ajout tâches (go/table/X).
- `update_robot_logic()` : Logique déplacements, états.
- `move_step()` : Animation pas à pas.
- `show_validation_popup()` : Popup confirmation livraison.
- `paintEvent(event)` : Rendu tables, chemins, robot.

### Fonctions utilitaires
- `broadcast(message)` : Diffusion messages clients.
- `ws_handler(ws, path, sim)` : Gestionnaire WebSocket.
- `get_local_ip()` : Détection IP locale serveur.
- `start_server(sim)` : Lancement serveur WebSocket.

## Protocoles supportés

### Messages entrants
- `go/table/X` : Déplacement table X (1-4).
- `emergency_stop` : Arrêt immédiat, vidage file.

### Messages sortants
- `arrived/table/X` : Arrivée table X.
- `arrived/bar` : Arrivée bar.
- `validated/X` : Confirmation livraison.

## Exemples d'utilisation

### Simulation robot
```bash
python simulation.py
```
- Interface graphique, envoi `go/table/1` pour déplacer.
- Validation livraison dans popup pour retour bar.

### Génération QR
```bash
python generate_qr.py
```
- Génère `qrcodes/table_1_test.png` avec URL locale.

### Scan réseau
```bash
python scan.py
```
- Ping IPs 10.42.0.1-254, affiche actives.

## Architecture technique

- **PyQt5** : Interface graphique simulation.
- **WebSockets** : Communication temps réel.
- **Threading** : Séparation UI et serveur.
- **QTimer** : Animation 30 FPS.
- **QRCode** : Génération avec correction erreur.
- **Subprocess** : Ping réseau scan.

## Installation et configuration

### Dépendances
```bash
pip install -r requirements.txt
```

### Configuration
- Copier `.env.example` vers `.env`.
- Adapter variables environnement test.

## Utilisation développement

### Tests WebSocket
- Lancer simulation comme serveur remplacement.
- Tester APK, site web, modules table contre serveur.
- Valider séquences : commande → déplacement → arrivée → validation → retour.

### Débogage réseau
- Utiliser `scan.py` vérifier connectivité hotspot.
- Générer QR tests accès client local.

### Simulation scénarios
- Tester files multiples.
- Simuler arrêts urgence.
- Valider chemins et timings.

## API du module

::: slaybot_utilitaire_dev.simulation

## Dépannage

- **Interface non affichée** : Vérifier PyQt5, display disponible.
- **WebSocket refuse** : Vérifier port 8765 libre.
- **Déplacements erratiques** : Vérifier TABLES, PATHS.
- **QR non scanné** : Augmenter box_size, error_correction.
