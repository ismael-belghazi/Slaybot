# slaybot_apk

Le module `slaybot_apk` contient l'application mobile Android développée avec Kivy, permettant de contrôler le robot SlayBot, de gérer les files de tâches et de suivre l'état du système en temps réel.

## Objectif

Fournir une interface mobile intuitive pour le personnel de salle afin de :
- Recevoir les notifications de commandes et nettoyages.
- Valider et dispatcher les missions du robot.
- Gérer les files d'attente et l'état du robot.
- Configurer la connexion au hotspot.
- Déclencher des arrêts d'urgence.

## Architecture

- `main.py` : Cœur de l'application avec classes RobotAPI, MainScreen, SettingsScreen.
- `buildozer.spec` : Configuration pour compilation APK avec Buildozer.
- `docker-compose.yaml` : Environnement de build isolé.
- `config.json` : Configuration persistante de l'IP hotspot.
- `requirements.txt` : Dépendances Python (Kivy, websocket-client).

## Classes et fonctions principales

### RobotAPI
Classe statique pour la communication WebSocket :
- `connect()` : Établit et maintient la connexion au hotspot.
- `send(cmd)` : Envoie des commandes (go/table/X, emergency_stop).

### MainScreen
Écran principal avec interface tactile :
- `notify_new_order(table_id)` : Ajoute commande à préparer.
- `notify_new_clean(table_id)` : Ajoute tâche nettoyage.
- `validate_order(task_name)` : Valide et envoie en queue.
- `validate_clean(task_name)` : Idem pour nettoyage.
- `add_to_queue(table_id, task_type)` : Gestion file robot.
- `on_mission_complete()` : Marque mission terminée.
- `emergency_stop()` : Arrêt d'urgence, vidage files.

### SettingsScreen
Configuration IP hotspot :
- `save_config(new_ip)` : Sauvegarde et reconnexion.

## États et files

- `orders_to_prepare` : Commandes en attente validation.
- `clean_tasks` : Demandes nettoyage.
- `queue` : Missions actives du robot.
- États : idle, moving, emergency.

## Communication WebSocket

### Messages reçus
- `order/table/X` : Nouvelle commande table X.
- `clean/table/X` : Demande nettoyage table X.
- `arrived/bar` : Robot revenu au bar.
- `emergency_stop` : Arrêt d'urgence.

### Messages envoyés
- `go/table/X` : Déplacement vers table X.
- `go/bar` : Retour au bar.
- `emergency_stop` : Signal urgence.

## Compilation APK

### Prérequis
- Docker, Buildozer configuré.

### Commandes
```bash
docker compose run --rm kivy-apk buildozer android debug
docker compose run --rm kivy-apk buildozer android release
```

## API du module

::: slaybot_apk.main

## Notes pratiques

- Configurer l'IP hotspot (défaut 192.168.137.173) dans paramètres.
- Files séparées pour commandes et nettoyages.
- Arrêt d'urgence vide toutes les files.
- Compatible avec simulateur pour tests.
