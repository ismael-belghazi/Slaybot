# slaybot_table

Le module `slaybot_table` contient le code de l’ESP32 qui permet à une table de demander un nettoyage et d’indiquer son état par LED.

## But du module

`slaybot_table` permet de :

- se connecter au hotspot SlayBot
- envoyer une demande de nettoyage via WebSocket
- afficher l’état de la table avec des LEDs
- gérer un cooldown après une mission

## Composants

- `table(esp32)-code-generique.py` : code principal MicroPython.
- `README.MD` : documentation locale complémentaire.

## API du module

::: slaybot_table.table_esp32_code_generique

## Câblage et utilisation

- Bouton : GPIO 4 vers GND.
- LED verte : GPIO 18.
- LED jaune : GPIO 19.

## Fonctionnement

- `connect_wifi()` connecte le module au réseau Slaybot.
- `listen_websocket()` écoute les messages du serveur.
- Le bouton envoie `clean/table/X` quand la table est disponible.
- `arrived/bar` déclenche un cooldown et indique la table indisponible.

## Notes

- Le champ `TABLE_ID` identifie chaque table.
- `WS_URL` doit pointer vers le hotspot.
- En cas d’erreur réseau, le module redémarre automatiquement.
