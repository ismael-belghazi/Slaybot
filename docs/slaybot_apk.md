# slaybot_apk

Le module `slaybot_apk` contient l'application mobile Android Kivy qui pilote le robot SlayBot et reçoit les notifications d'état.

## But du module

`slaybot_apk` sert à :

- recevoir des ordres de service et des notifications du hotspot
- gérer une file de missions robot
- valider ou relancer des tâches de nettoyage et de livraison
- configurer l'adresse du hotspot

## Architecture

- `main.py` : logique Kivy, client WebSocket et interface utilisateur.
- `buildozer.spec` : configuration de compilation Android.
- `config.json` : adresse du serveur et paramètres de connexion.

## Comportements principaux

- `RobotAPI.connect()` ouvre et maintient la connexion WebSocket.
- `RobotAPI.send(cmd)` transmet les commandes au hotspot.
- `MainScreen` gère la display des missions, des files et du statut.
- `SettingsScreen.save_config()` enregistre l’IP et reconnecte l’application.

## API du module

::: slaybot_apk.main

## Notes pratiques

- Vérifier l’IP du hotspot avant de lancer l’application.
- Le module maintient une liste `orders_to_prepare` et une `queue` de missions.
- L’opération `emergency_stop()` vide la file et envoie `go/bar` au serveur.
- Le simulateur et le mode réel doivent partager les mêmes conventions de message WebSocket.
