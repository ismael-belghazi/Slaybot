
# Robot-Server & RSapp

Ce projet est un système complet de gestion pour un **robot de service en restaurant**. Il comprend une application mobile de commande (**RSapp**) développée avec **Kivy** et un simulateur de trajectoire visuel développé avec **PyQt5**. L'ensemble communique en temps réel via le protocole **WebSocket**.

## Sommaire

* [Aperçu du système](#aperçu-du-système)
* [Installation et Dépendances](#installation-et-dépendances)
* [Le Simulateur (Serveur PC)](#le-simulateur-serveur-pc)
* [L’Application Mobile (Client Android)](#lapplication-mobile-client-android)
* [Compilation de l’APK (Buildozer)](#compilation-de-lapk-buildozer)
* [Protocole de Communication](#protocole-de-communication)
* [Architecture du Projet](#architecture-du-projet)

---

## Aperçu du système

1.  **Le Serveur (PC/Simulateur)** : Centralise les commandes, gère la file d'attente des livraisons et simule visuellement le déplacement du robot sur un plan (Tables T1 à T4 et le Bar).
2.  **Le Client (Smartphone Android)** : Interface utilisateur permettant d'envoyer le robot vers une table spécifique ou de déclencher un arrêt d'urgence.
3.  **Communication** : Flux bidirectionnel. Le client envoie des ordres (`go/T1`), le serveur renvoie des confirmations d'état (`arrived/table/1`).

---

## Installation et Dépendances

### Configuration du PC (Simulateur)
Le simulateur nécessite Python 3.10+ et les bibliothèques suivantes :
* **PyQt5** : Pour l'interface graphique et le rendu 2D du robot.
* **websockets** : Pour la gestion du serveur de communication.
* **asyncio** : Pour le traitement asynchrone des messages.

Installation rapide :
`pip install PyQt5 websockets`

### Configuration Mobile (Application)
L'application est compilée pour Android, mais pour le développement local, elle nécessite :
* **Kivy** : Framework de l'interface utilisateur.
* **websocket-client** : Pour la connexion au serveur.
* **requests** : Pour les appels API complémentaires.

---

## Le Simulateur (Serveur PC)

Le simulateur joue le rôle de "cerveau" du robot. Il affiche une carte avec 4 tables et une zone de bar.

**Lancement :**
`python simulation.py`

**Fonctionnalités clés :**
* **Auto-détection IP** : Le serveur identifie automatiquement l'IP locale du PC (ex: 192.168.1.x) pour permettre la connexion du smartphone.
* **Gestion de file d'attente** : Si plusieurs tables sont demandées, le robot les traite l'une après l'autre.
* **Validation de livraison** : À l'arrivée à une table, une fenêtre surgissante (Popup) demande la validation manuelle avant que le robot ne retourne au bar.
* **Retour intelligent** : Le robot emprunte le chemin inverse exact pour revenir à sa base.

---

## L’Application Mobile (Client Android)

L'interface **RSapp** permet au personnel de salle de piloter le robot à distance.

**Fonctions disponibles :**
* **Connexion IP** : Saisie de l'adresse IP affichée sur le simulateur.
* **Contrôle de destination** : Boutons dédiés pour envoyer le robot aux tables 1, 2, 3 ou 4.
* **Statut en direct** : Affichage des messages de retour (ex: "Robot en route vers T1", "Livraison arrivée").
* **Arrêt d'urgence** : Bouton prioritaire pour stopper immédiatement tous les mouvements.

---

## Compilation de l’APK (Buildozer)

La génération de l'application Android utilise **Buildozer**. La configuration est optimisée pour les versions récentes d'Android (API 33).

### Détails du Build (buildozer.spec)
* **SDK Cible** : Android 13 (API 33).
* **NDK** : 25b.
* **Architectures** : arm64-v8a (64-bit) et armeabi-v7a (32-bit).
* **Exigences critiques** : `python3, kivy, openssl, websocket-client, requests`.

### Commandes de génération
`buildozer android debug`

*Note : La première compilation télécharge et compile OpenSSL, ce qui peut prendre environ 20 minutes.*

---

## Protocole de Communication

Les échanges se font par chaînes de caractères simples via WebSocket :

* **Client → Serveur** :
  -  `go/1` à `go/4` : Envoie le robot à une table.
  - `emergency` : Vide la file d'attente et stoppe le mouvement.

* **Serveur → Client** :
  - `arrived/table/X` : Notifie que le robot est devant la table.
  - `validated/X` : Confirme que la commande a été récupérée.
  - `arrived/bar` : Notifie que le robot est revenu à sa base.

---

## Architecture du Projet

* **main.py** : Code source de l'application mobile Kivy.
* **simulation.py** : Code source du simulateur PyQt5 et du serveur WebSocket.
* **buildozer.spec** : Fichier de configuration pour la compilation Android.
---

## Améliorations possibles

* **Évitement d'obstacles** : Intégration de capteurs simulés sur le tracé.
* **Multi-robots** : Gestion de plusieurs instances de robots sur le même plan.
* **Base de données** : Historique des temps de livraison et statistiques de service.