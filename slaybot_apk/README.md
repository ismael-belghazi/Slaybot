# slaybot_apk

Ce module contient l’application Android de contrôle du robot, développée avec Kivy et utilisable sur un smartphone.

## Objectif

Permettre au personnel de salle de piloter le robot, d’envoyer des commandes aux tables, de gérer les nettoyages et de suivre l’état en temps réel.

## Fichiers principaux

- `main.py` : logique de l’application.
- `buildozer.spec` : configuration de compilation Android.
- `docker-compose.yaml` : environnement de build Buildozer.
- `requirements.txt` : dépendances Python.

## Fonctionnement

### WebSocket

`main.py` ouvre une connexion WebSocket vers le hotspot SlayBot.
Il accepte plusieurs formats de messages :

- `order/table/X` ou `ORD Table X`
- `clean/table/X` ou `CLEAN Table X`
- `cancel/table/X` ou `CANCEL Table X`
- `ready/table/X` ou `READY Table X`
- `paid/table/X` ou `PAID Table X`
- `arrived/bar`

### Interface

- `orders_to_prepare` : commandes en attente.
- `clean_tasks` : demandes de nettoyage.
- `queue` : file des actions à exécuter.
- Une commande confirmée est envoyée au hotspot dès qu’elle atteint la tête de file.

## Compilation APK

### Pré-requis

- Docker et Docker Compose.
- Buildozer configuré dans `buildozer.spec`.

### Commande

```bash
docker compose run --rm kivy-apk buildozer android debug
```

## Conseils

- Tester la connexion WebSocket avec l’adresse `10.42.0.1:8765` avant de compiler.
- Vérifier les logs du build pour détecter les dépendances manquantes.
- Ne pas modifier `source.include_exts` sans connaître l’impact sur le packaging.
