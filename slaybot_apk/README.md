# slaybot_apk

Ce module contient l'application Android de contrôle du robot SlayBot, développée avec Kivy. Elle permet au personnel de salle de piloter le robot, d'envoyer des commandes aux tables, de gérer les nettoyages et de suivre l'état en temps réel via une interface mobile intuitive.

## Objectif

Fournir une interface mobile pour la gestion opérationnelle du robot dans un environnement de restaurant : réception des demandes de service, programmation des missions, suivi du statut du robot, et arrêt d'urgence.

## Fichiers principaux

- `main.py` : Logique principale de l'application Kivy, gestion WebSocket et interface utilisateur.
- `buildozer.spec` : Configuration pour la compilation en APK Android avec Buildozer.
- `docker-compose.yaml` : Environnement de build isolé pour Buildozer.
- `dockerfile` : Image Docker pour le build.
- `requirements.txt` : Dépendances Python (Kivy, websocket-client).
- `config.json` : Configuration persistante de l'IP du hotspot.
- `my-release-key.keystore` : Clé de signature pour les APK de production.

## Fonctionnalités principales

- **Connexion WebSocket** : Communication temps réel avec le hotspot SlayBot pour recevoir les notifications (commandes, nettoyages, paiements).
- **Gestion des tâches** : Files séparées pour commandes à préparer, nettoyages, et queue d'exécution du robot.
- **Interface tactile** : Écrans pour valider les tâches, programmer manuellement, suivre le statut, et configurer l'IP.
- **Arrêt d'urgence** : Bouton pour stopper immédiatement toutes les opérations.
- **Navigation programmée** : Envoi du robot vers tables spécifiques ou bar.

## Classes et fonctions importantes

### RobotAPI
Classe statique pour la gestion WebSocket :
- `connect()` : Établit la connexion au hotspot.
- `send(cmd)` : Envoie une commande au robot.
- Gestion des callbacks pour mises à jour d'état.

### MainScreen
Écran principal de l'application :
- `notify_new_order(table_id)` : Ajoute une commande à préparer.
- `notify_new_clean(table_id)` : Ajoute une tâche de nettoyage.
- `validate_order(task_name)` : Valide une commande et l'envoie en queue.
- `validate_clean(task_name)` : Valide un nettoyage et l'envoie en queue.
- `add_to_queue(table_id, task_type)` : Ajoute une mission à la file du robot.
- `on_mission_complete()` : Marque la mission courante comme terminée.
- `emergency_stop()` : Arrêt d'urgence, vide toutes les files.
- `go_to_bar()` : Envoie le robot au bar.

### SettingsScreen
Écran de configuration :
- `save_config(new_ip)` : Sauvegarde l'IP du hotspot dans config.json.

### RobotApp
Classe principale de l'application Kivy :
- Charge la configuration au démarrage.
- Initialise la connexion WebSocket.

## Exemples d'utilisation

### Réception d'une commande
1. Notification WebSocket : `order/table/5`
2. Ajout à `orders_to_prepare` : "ORD Table 5"
3. Personnel valide via bouton "PRÊT"
4. Envoi en queue : robot se déplace vers table 5
5. À l'arrivée : `arrived/bar` marque la mission terminée

### Programmation manuelle
1. Appui sur "Commander" ou "Nettoyer"
2. Sélection de la table (1-4)
3. Ajout direct en queue sans validation préalable

### Gestion d'urgence
- Bouton rouge "STOP" : vide toutes les files, envoie "emergency_stop" au robot, met à jour le statut.

## Architecture technique

- **Framework** : Kivy pour l'interface multiplateforme (Android/iOS).
- **Communication** : WebSocket pour échanges bidirectionnels avec le hotspot.
- **Persistance** : JSON pour configuration IP.
- **Threading** : Connexion WebSocket en thread séparé pour éviter le blocage UI.
- **UI** : KV language pour la définition déclarative de l'interface (boutons, labels, layouts).

## Compilation APK

### Prérequis
- Docker et Docker Compose installés.
- Buildozer configuré (voir `buildozer.spec` pour les permissions Android).

### Commande de build
```bash
docker compose run --rm kivy-apk buildozer android debug
```

### APK de production
```bash
docker compose run --rm kivy-apk buildozer android release
```

L'APK généré se trouve dans le dossier `bin/`.

## Conseils

- Assurez-vous que l'IP du hotspot est correctement configurée dans les paramètres.
- L'application gère automatiquement la reconnexion en cas de perte de connexion.
- Utilisez l'arrêt d'urgence uniquement en cas de nécessité pour éviter les interruptions de service.

- Tester la connexion WebSocket avec l’adresse `10.42.0.1:8765` avant de compiler.
- Vérifier les logs du build pour détecter les dépendances manquantes.
- Ne pas modifier `source.include_exts` sans connaître l’impact sur le packaging.

