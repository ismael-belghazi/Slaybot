# slaybot_table

Le module `slaybot_table` fournit le code MicroPython pour les dispositifs de table ESP32, permettant aux clients de signaler des besoins de nettoyage ou de service via un bouton physique, avec retour visuel par LEDs.

## Objectif

Implémenter un système simple et robuste pour les tables de restaurant : bouton d'appel pour nettoyage, indication visuelle de l'état, communication WebSocket avec le serveur central, et gestion automatique des périodes de cooldown.

## Fichiers principaux

- `table_esp32_code_generique.py` : Code MicroPython pour ESP32 avec gestion WiFi, WebSocket et GPIO.
- `README.MD` : Documentation du module.

## Fonctionnalités principales

- **Bouton d'appel** : Détection d'appui avec anti-rebond pour éviter les faux positifs.
- **Indicateurs LEDs** : LED verte (disponible), LED jaune (occupé/cooldown).
- **Connexion WiFi** : Connexion automatique au hotspot Slaybot.
- **Communication WebSocket** : Envoi de demandes de nettoyage, réception de confirmations.
- **Gestion d'état** : États commande en cours, cooldown, disponible.
- **Redémarrage automatique** : Reset en cas d'erreur de connexion.

## Classes et fonctions importantes

### Fonctions principales
- `set_led_state(vert_on)` : Contrôle des LEDs (vert/jaune).
- `leds_off()` : Extinction des LEDs.
- `connect_wifi()` : Connexion au réseau WiFi Slaybot.
- `listen_websocket(ws)` : Écoute des messages du serveur (arrivée robot).
- `main()` : Boucle principale avec gestion états et bouton.

### Variables d'état
- `commande_en_cours` : Booléen pour mission active.
- `periode_reset` : Booléen pour cooldown post-mission.
- `ms_fin_mission` : Timestamp fin de mission pour calcul cooldown.

## Configuration matérielle

### Câblage ESP32
- **Bouton** : GPIO 4 connecté à GND (pull-up interne).
- **LED verte** : GPIO 18 (service disponible).
- **LED jaune** : GPIO 19 (service demandé/cooldown).
- **Alimentation** : 3.3V/5V selon ESP32.

### Paramètres configurables
- `TABLE_ID` : Identifiant unique de la table (défaut "1").
- `PIN_LED_VERT` : GPIO pour LED verte (défaut 18).
- `PIN_LED_JAUNE` : GPIO pour LED jaune (défaut 19).
- `PIN_BOUTON` : GPIO pour bouton (défaut 4).
- `DELAI_RESET` : Durée cooldown en ms (défaut 20000 = 20s).

## Protocoles de communication

### Messages sortants (vers serveur)
- `clean/table/{TABLE_ID}` : Demande de nettoyage lors d'appui bouton.

### Messages entrants (du serveur)
- `arrived/bar` : Confirmation retour robot au bar, déclenche cooldown.

## États et comportements

### État disponible
- LED verte allumée.
- Bouton actif : envoi `clean/table/X`, passage en état occupé.

### État occupé
- LED jaune allumée.
- Bouton désactivé.
- Attente message `arrived/bar`.

### État cooldown
- LED jaune allumée.
- Bouton désactivé.
- Durée : 20 secondes après `arrived/bar`.
- Retour automatique à disponible.

## Exemples d'utilisation

### Séquence normale
1. Table disponible : LED verte.
2. Client appuie bouton : envoi WebSocket, LED jaune.
3. Robot arrive, nettoie, repart.
4. Serveur envoie `arrived/bar` : début cooldown 20s, LED jaune.
5. Fin cooldown : LED verte, prêt pour nouvelle demande.

### Gestion d'erreur
- Perte connexion : LEDs éteintes, tentative reconnexion, reset automatique.

## Architecture technique

- **MicroPython** : Environnement Python pour ESP32.
- **uasyncio** : Programmation asynchrone pour WebSocket et WiFi.
- **GPIO** : Contrôle direct des pins pour LEDs et bouton.
- **WebSocket** : Protocole de communication temps réel.
- **Anti-rebond** : Délai 500ms après appui bouton.

## Déploiement

### Prérequis
- ESP32 avec MicroPython installé.
- Accès au hotspot Slaybot (SSID: "Slaybot", password: "MHI-Hotspot").

### Installation
1. Copier `table_esp32_code_generique.py` vers ESP32 comme `main.py`.
2. Modifier `TABLE_ID` si nécessaire.
3. Redémarrer ESP32.

### Personnalisation
- Adapter pins GPIO selon câblage.
- Modifier `DELAI_RESET` pour ajuster cooldown.
- Changer `SSID`/`PASSWORD` si réseau différent.

## Dépannage

- **LEDs ne s'allument pas** : Vérifier câblage et alimentation.
- **Bouton non réactif** : Tester continuité GPIO4-GND.
- **Connexion WiFi échoue** : Vérifier portée hotspot, credentials.
- **Messages non reçus** : Surveiller logs série (115200 bauds).
- **Reset fréquent** : Vérifier stabilité réseau, firmware MicroPython.

