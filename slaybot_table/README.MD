# README - SlayBot Table Client (ESP32)

> Ce dépôt contient le code MicroPython destiné aux modules installés sur les tables des clients. Ce système permet d'appeler le robot via un bouton physique et de suivre l'état de la demande grâce à un retour visuel par LEDs.


## Fonctionnalités

* Connexion WiFi Automatique : Se connecte au hotspot Slaybot (10.42.0.1) dès le démarrage.
* Système d'Appel : Envoie une requête WebSocket au serveur central lors de l'appui sur le bouton.
* Gestion d'États par LEDs :
  - LED Verte : Table disponible, prête à appeler le robot.
  - LED Jaune : Commande en cours ou période de cooldown.
* Cooldown de Sécurité : Après chaque mission terminée, le module bloque les nouveaux appels pendant 20 secondes pour éviter les doublons.
* Auto-Réparation : En cas de perte de connexion ou d'erreur critique, l'ESP32 redémarre automatiquement.


## Schéma de Câblage (ESP32)

* Bouton Poussoir : Connecté entre le GPIO 4 et le GND (Utilise la résistance de Pull-Up interne).
* LED Verte : Connectée au GPIO 18 (avec résistance de 220 ohms).
* LED Jaune : Connectée au GPIO 19 (avec résistance de 220 ohms).


## Protocole de Communication

>Le module communique avec le serveur central (Raspberry Pi) via WebSockets :

* Sortie (Appel) : Envoie la chaîne de caractères "clean/table/X" (où X est l'ID de la table).
* Entrée (Retour) : Écoute le message "arrived/bar" pour savoir quand le robot a terminé sa mission et déclencher le cooldown de 20 secondes.



## Installation et Utilisation

1. Pré-requis : Flasher l'ESP32 avec le firmware MicroPython et installer une bibliothèque client WebSocket (comme micro_websockets).
2. Configuration : Modifier la variable TABLE_ID dans le code pour identifier chaque table de manière unique (1, 2, 3...).
3. Transfert : Copier le script sur l'ESP32 en le nommant main.py pour un lancement automatique.
4. Statut : Au démarrage, les LEDs s'allument selon la réussite de la connexion au serveur central.



## Maintenance

* WiFi : Si la LED reste éteinte, vérifiez que le hotspot du Raspberry Pi "Cerveau" est bien actif.
* Logs : Les erreurs et états de connexion sont affichés en temps réel sur le port série (Baud 115200).



SlayBot Project - 2026 ©