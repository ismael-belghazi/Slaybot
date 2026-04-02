# README - Slaybot Utilitaires de Développement

>Cette section regroupe les outils de simulation et de test pour l'écosystème Slaybot. L'outil principal est le Simulateur de Robot Restaurant, qui permet de valider la logique de communication et le comportement du serveur central avant le déploiement sur matériel réel.

## Simulateur de Robot (Python et PyQt5)

>Ce script simule un robot dans un environnement de restaurant avec 4 tables et un bar. Il intègre un serveur WebSocket complet qui réagit aux commandes réelles de l'APK ou des modules de table.

### Fonctionnalités principales

* Visualisation temps réel : Déplacement fluide du robot sur une carte 2D représentant la salle.
* Serveur WebSocket intégré : Écoute sur le port 8765 et accepte les connexions entrantes.
* Gestion de file d'attente : Empile les commandes de livraison si plusieurs tables appellent simultanément.
* Logique de trajet : Calcule les chemins aller-retour entre le Bar et les différentes Tables.
* Popup de validation : Simule l'interaction humaine pour confirmer la bonne réception d'une commande.

## Installation et Lancement

### 1. Pré-requis
>Assurez-vous d'avoir Python installé, puis installez les bibliothèques nécessaires via pip install PyQt5 websockets.

### 2. Lancement
>Exécutez le script depuis votre terminal avec la commande python simulateur_robot.py.

## Protocole de Communication (Tests)

>Le simulateur réagit aux mêmes messages que le robot réel. Vous pouvez tester la connexion en envoyant des chaînes de caractères brutes via un client WebSocket.

* Messages reçus par le simulateur :
  -   go/1 (ou go/T1) : Ajoute la Table 1 à la file d'attente et lance le trajet.
  - emergency : Arrête immédiatement le robot et vide la file d'attente.

* Messages envoyés par le simulateur (Broadcast) :
  - arrived/table/T1 : Envoyé quand le robot atteint sa destination.
  - validated/T1 : Envoyé quand l'utilisateur clique sur OK dans la fenêtre de livraison.
  - arrived/bar : Envoyé quand le robot est revenu à son point de départ.

## Configuration de la Carte

> Les coordonnées et les chemins sont définis dans les dictionnaires TABLES et PATHS au début du script. Vous pouvez modifier ces points pour adapter la simulation à une nouvelle disposition de salle.

* Vitesse : Ajustable via la constante SPEED.
* Points de passage : Modifiables dans PATHS pour créer des virages ou éviter des obstacles virtuels.

## Notes de Développement

* IP du Serveur : Le simulateur affiche automatiquement l'adresse IP locale à laquelle vos autres appareils (APK ou ESP32) doivent se connecter.
* Thread de Réseau : Le serveur WebSocket tourne dans un thread séparé pour ne pas bloquer l'interface graphique PyQt5.

SlayBot Project - 2026 ©