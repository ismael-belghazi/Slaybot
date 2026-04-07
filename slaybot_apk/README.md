# RSapp – Robot Service App

> Ce projet est une **application mobile de contrôle pour un robot de service en restaurant**. L’application permet au personnel de salle de piloter le robot à distance et de suivre l’état des commandes en temps réel via **WebSocket**.

## Sommaire

* [Aperçu du système](#aperçu-du-système)
* [Installation et dépendances](#installation-et-dépendances)
* [Fonctions principales de l’application](#fonctions-principales-de-lapplication)
* [Compilation de l’APK (Buildozer)](#compilation-de-lapk-buildozer)
* [Protocole de communication](#protocole-de-communication)
* [Architecture du projet](#architecture-du-projet)



## Aperçu du système

1. **Client (smartphone Android)** : Interface utilisateur permettant d’envoyer le robot vers une table spécifique ou de déclencher un arrêt d’urgence.
2. **Communication bidirectionnelle** : Le client envoie des ordres (`go/1` à `go/4`), le serveur renvoie des confirmations d’état (`arrived/table/1`).


## Installation et dépendances

Pour le développement local ou les tests avant compilation :

* **Python 3.10+**
* **Kivy** : Framework de l’interface utilisateur.
* **websocket-client** : Pour la connexion au serveur.
* **requests** : Pour les appels API complémentaires.

> Installation rapide :

```bash
pip install kivy websocket-client requests
```



## Fonctions principales de l’application

* **Connexion IP** : Saisie de l’adresse IP du serveur robot.
* **Contrôle de destination** : Boutons dédiés pour envoyer le robot aux tables 1 à 4.
* **Statut en direct** : Affichage des messages de retour (ex : "Robot en route vers T1", "Livraison arrivée").
* **Arrêt d’urgence** : Bouton prioritaire pour stopper immédiatement tous les mouvements.
* **Programmation manuelle** : Possibilité de planifier une commande ou un nettoyage directement depuis l’interface.


## Compilation de l’APK (Buildozer)

> La génération de l’application Android utilise **Buildozer**, optimisée pour Android 13 (API 33).

### Détails du build (`buildozer.spec`)

* **SDK cible** : Android 13 (API 33)
* **NDK** : 25b
* **Architectures** : arm64-v8a (64-bit) et armeabi-v7a (32-bit)
* **Exigences critiques** : `python3, kivy, openssl, websocket-client, requests`

### Commandes de génération

```bash
docker compose run --rm kivy-apk buildozer android debug
```

> Note : La première compilation télécharge et compile OpenSSL, ce qui peut prendre environ 20 minutes.


## Protocole de communication

Les échanges se font via WebSocket avec des chaînes de caractères simples :

* **Client → Serveur** :

  * `go/1` à `go/4` : Envoie le robot à une table.
  * `emergency` : Vide la file d’attente et stoppe le mouvement.

* **Serveur → Client** :

  * `arrived/table/X` : Notifie que le robot est devant la table.
  * `validated/X` : Confirme que la commande a été récupérée.
  * `arrived/bar` : Notifie que le robot est revenu à sa base.


## Architecture du projet

* **main.py** : Code source de l’application mobile Kivy.
* **buildozer.spec** : Fichier de configuration pour la compilation Android.


**SlayBot Project – 2026 ©**

