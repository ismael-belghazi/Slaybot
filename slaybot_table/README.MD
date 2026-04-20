# slaybot_table

Le module `slaybot_table` réunit le code MicroPython pour les boutons de table et les retours LEDs.

## Objectif

Permettre à un client de table de demander le robot ou le nettoyage, avec un retour visuel immédiat.

## Fichiers

- `table(esp32)-code-generique.py` : script principal pour l’ESP32.
- `README.MD` : documentation du module.

## Câblage

- Bouton : GPIO 4 vers GND.
- LED verte : GPIO 18.
- LED jaune : GPIO 19.

## Fonctionnement

- Appui sur le bouton : envoi d’un message WebSocket au serveur.
- LED verte : état prêt.
- LED jaune : commande en cours ou période de cooldown.
- Cooldown : 20 secondes après chaque mission.

## Déploiement

1. Installer MicroPython sur l’ESP32.
2. Copier `table(esp32)-code-generique.py` en `main.py`.
3. Configurer l’identifiant de table si nécessaire.
4. Redémarrer l’ESP32.

## Protocoles

- Message sortant : `clean/table/X`.
- Message entrant : `arrived/bar`.

## Conseils

- Tester la connexion au hotspot SlayBot.
- Surveiller le port série à 115200 bauds pour les logs.
