# slaybot_table

Le module `slaybot_table` fournit le code MicroPython pour les dispositifs ESP32 des tables, permettant aux clients de signaler des besoins de nettoyage via un bouton physique avec retour visuel par LEDs.

## Objectif

Implémenter un système simple et robuste pour les tables :
- Bouton d'appel pour nettoyage/service.
- Indicateurs LEDs (vert = disponible, jaune = occupé/cooldown).
- Connexion WiFi automatique au hotspot.
- Communication WebSocket pour demandes et confirmations.
- Gestion cooldown post-mission.

## Composants

- `table_esp32_code_generique.py` : Code MicroPython ESP32.
- `README.MD` : Documentation locale.

## Classes et fonctions principales

### Fonctions principales
- `set_led_state(vert_on)` : Contrôle LEDs.
- `leds_off()` : Extinction LEDs.
- `connect_wifi()` : Connexion réseau Slaybot.
- `listen_websocket(ws)` : Écoute messages serveur.
- `main()` : Boucle principale gestion états.

### Variables d'état
- `commande_en_cours` : Mission active.
- `periode_reset` : Cooldown post-mission.
- `ms_fin_mission` : Timestamp fin mission.

## Configuration matérielle

### Câblage ESP32
- **Bouton** : GPIO 4 à GND (pull-up interne).
- **LED verte** : GPIO 18 (service disponible).
- **LED jaune** : GPIO 19 (occupé/cooldown).
- **Alimentation** : 3.3V/5V selon ESP32.

### Paramètres configurables
- `TABLE_ID` : ID unique table (défaut "1").
- `PIN_LED_VERT/JAUNE/BOUTON` : GPIOs.
- `DELAI_RESET` : Cooldown ms (défaut 20000).

## Protocoles communication

### Messages sortants
- `clean/table/{TABLE_ID}` : Demande nettoyage.

### Messages entrants
- `arrived/bar` : Fin mission, début cooldown.

## États et comportements

### État disponible
- LED verte allumée.
- Bouton actif : envoi WebSocket, passage occupé.

### État occupé
- LED jaune allumée.
- Bouton désactivé.
- Attente `arrived/bar`.

### État cooldown
- LED jaune allumée.
- Bouton désactivé.
- Durée 20s après `arrived/bar`.
- Retour automatique disponible.

## Exemples d'utilisation

### Séquence normale
1. Table disponible : LED verte.
2. Appui bouton : envoi `clean/table/1`, LED jaune.
3. Robot arrive, nettoie, repart.
4. Serveur envoie `arrived/bar` : cooldown 20s, LED jaune.
5. Fin cooldown : LED verte, prête.

### Gestion erreur
- Perte connexion : LEDs éteintes, reconnexion, reset auto.

## Architecture technique

- **MicroPython** : Python pour ESP32.
- **uasyncio** : Programmation asynchrone.
- **GPIO** : Contrôle direct pins.
- **WebSocket** : Communication temps réel.
- **Anti-rebond** : Délai 500ms appui bouton.

## Déploiement

### Prérequis
- ESP32 avec MicroPython.
- Accès hotspot Slaybot.

### Installation
1. Copier `table_esp32_code_generique.py` comme `main.py`.
2. Modifier `TABLE_ID` si besoin.
3. Redémarrer ESP32.

### Personnalisation
- Adapter GPIOs selon câblage.
- Modifier `DELAI_RESET` pour cooldown.

## API du module

::: slaybot_table.table_esp32_code_generique

## Dépannage

- **LEDs non allumées** : Vérifier câblage/alimentation.
- **Bouton non réactif** : Tester continuité GPIO4-GND.
- **Connexion échoue** : Vérifier portée hotspot, credentials.
- **Messages non reçus** : Surveiller logs série (115200 bauds).
