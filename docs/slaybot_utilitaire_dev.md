# slaybot_utilitaire_dev

Le module `slaybot_utilitaire_dev` contient des outils de simulation et de test pour piloter SlayBot sans matériel réel.

## But du module

`slaybot_utilitaire_dev` permet de :

- simuler le déplacement du robot
- tester la réception d’événements WebSocket
- valider les protocoles `go/X`, `validated/T` et l’ordre des commandes
- développer sans hotspot physique

## Composants

- `simulation.py` : simulateur Qt et serveur WebSocket.
- `generate_qr.py` : utilitaire de génération de QR codes.
- `requirements.txt` : dépendances Python.
- `.env` / `.env.exmple` : configuration de simulation.

## API du module

::: slaybot_utilitaire_dev.simulation

## Fonctionnement

- `RobotSimulator` affiche la position du robot sur un plan de restaurant.
- `add_task()` ajoute un nouveau trajet à la file en fonction du message.
- `broadcast()` diffuse les événements aux clients connectés.
- `ws_handler()` gère les connexions WebSocket entrantes.

## Avantages

- Permet de tester `APK -> hotspot -> robot` sans matériel réel.
- Visualise la file d’attente et les trajectoires.
- Facilement extensible pour de nouveaux scénarios.
