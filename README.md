# MASTER README - SlayBot Ecosystem

> Ce document centralise la documentation de l'ensemble du projet **SlayBot**, un système robotique complet pour le service en restaurant. Le projet est divisé en cinq modules interconnectés communiquant en temps réel via WebSockets.


## Présentation Générale

>SlayBot est une solution de service automatisée comprenant :
1.  **Le Cerveau (Hotspot)** : Un Raspberry Pi central gérant le réseau et la logique.
2.  **L'Interface Mobile (APK)** : Une application pour envoyer le robot en mission.
3.  **L'Interface Robot (Screen)** : Un écran tactile affichant le visage et les interactions du robot.
4.  **Les Modules Table** : Des boîtiers ESP32 permettant aux clients d'appeler le robot.
5.  **Le Simulateur** : Un outil PC pour tester la logique sans matériel physique.


## 1. Slaybot APK (Application de Commande)

>Situé dans le dossier `slaybot_apk`, ce module est l'interface de pilotage pour le personnel.

* **Technologie** : Python / Kivy.
* **Fonctions** : Connexion à l'IP du cerveau, envoi du robot aux tables 1 à 4, arrêt d'urgence.
* **Compilation** : Utilise Buildozer via Docker pour générer l'APK Android (API 33).
* **Commande de build** : docker compose run --rm kivy-apk buildozer android debug.


## 2. Slaybot Hotspot (Le Cerveau Central)

>Situé dans le dossier `slaybot_hotspot`, c'est le centre nerveux installé sur une Raspberry Pi.

* **Réseau** : Crée un Wi-Fi privé nommé Slaybot (IP 10.42.0.1).
* **Serveur** : Gère un serveur WebSocket sur le port 8765.
* **Installation** : Script install.sh automatisé pour configurer NetworkManager et le service robot.service.
* **Fiche Technique** : SSID : Slaybot | MDP : MHI-Hotspot | Port : 8765.



## 3. Slaybot Screen (Interface Visuelle)

>Situé dans le dossier `slaybot_screen`, ce module gère l'écran fixé sur le robot.

* **Technologie** : Python / Tkinter.
* **Visage Dynamique** : Affiche des expressions (Heureux, Étonné, Erreur) selon l'état du trajet.
* **Interaction** : Bouton vert de confirmation de réception et bouton rouge d'arrêt d'urgence.
* **Auto-Run** : Configuré via un service systemd pour se lancer au démarrage de l'écran.



## 4. Slaybot Table (Appel Client)

>Situé dans le dossier `slaybot_table`, ce code équipe les modules ESP32 sur chaque table.

* **Technologie** : MicroPython.
* **Matériel** : ESP32 + Bouton poussoir + LED Verte (Prêt) + LED Jaune (Occupé).
* **Logique** : Envoie une requête d'appel au cerveau. Gère un cooldown de 20 secondes après chaque mission pour éviter les doublons.
* **Câblage** : Bouton (GPIO 4), LED Verte (GPIO 18), LED Jaune (GPIO 19).


## 5. Slaybot Utilitaires (Développement & Tests)

>Situé dans le dossier `slaybot_utilitaire_dev`, cet outil permet de simuler le comportement du robot sur PC.

* **Technologie** : Python / PyQt5.
* **Simulation 2D** : Visualise le robot se déplaçant entre le Bar et les Tables sur un plan réel.
* **Test Réseau** : Simule le serveur central, permettant de connecter l'APK ou les ESP32 directement à votre ordinateur pour débogage.
* **Lancement** : python simulateur_robot.py.


## Protocole de Communication Global

>Tous les modules utilisent des messages texte ou JSON via WebSocket pour échanger des informations :

### Commandes (Sortie)
* go/X : Envoie le robot à la table X (depuis l'APK ou le Simulateur).
* order/table/X : Requête d'appel depuis une table client (ESP32).
* emergency : Arrêt immédiat de tous les systèmes.

### Retours d'état (Entrée)
* arrived/table/X : Le robot est arrivé à destination.
* arrived/bar : Le robot est revenu à sa base.
* validated/X : La commande a été récupérée par le client.


## Architecture des Dossiers

/ (Racine du Projet)
├── slaybot_apk/          # Code Kivy et Buildozer
├── slaybot_hotspot/      # Configuration Serveur et Wi-Fi RPi
├── slaybot_screen/       # Interface graphique du visage
├── slaybot_table/        # Code MicroPython pour ESP32
└── slaybot_utilitaire_dev/ # Simulateur PyQt5 de test

SlayBot Project - 2026 ©