# slaybot_hotspot

Le module `slaybot_hotspot` fournit le hotspot Wi-Fi et le serveur WebSocket central du système SlayBot.

## But du module

`slaybot_hotspot` centralise la communication entre :

- l’application Android (`slaybot_apk`)
- l’interface robot embarquée (`slaybot_screen`)
- les modules table ESP32 (`slaybot_table`)
- le site de commande web (`site_commande`)

## Composants

- `install.sh` : script d'installation du hotspot.
- `serveur_cerveau.py` : serveur WebSocket principal.
- `robot.service` : configuration systemd.
- `requirements.txt` : dépendances Python.

## Installation

1. Copier les fichiers sur le Raspberry Pi.
2. Rendre le script exécutable :

```bash
chmod +x install.sh
```

3. Lancer l'installation :

```bash
./install.sh
```

4. Choisir l'option `0` pour activer le hotspot.

## Fonctionnement du serveur

- Écoute WebSocket sur `0.0.0.0:8765`.
- Diffuse les messages reçus à tous les clients connectés.
- Gère les commandes selon leur préfixe.

## API du module

::: slaybot_hotspot.serveur_cerveau

## Messages supportés

- `go/X` : déplacement vers la table X
- `clean/table/X` : demande de nettoyage via table X
- `order/table/X` : nouvelle commande de la table X
- `ready/table/X` : notification de préparation
- `cancel/table/X` : annulation de commande
- `paid/table/X` : paiement confirmé

## Notes de maintenance

- `broadcast(message)` envoie le message à tous les clients actifs.
- `piloter_deplacement(table_id)` exécute `pilote.py` et notifie le retour du robot.
- `get_local_ip()` indique l’adresse utilisable du serveur.

## Architecture réseau

- Le hotspot fournit une adresse IP fixe `10.42.0.1`.
- Les clients (APK, écran, ESP32) se connectent à ce réseau privé.
- Le serveur peut diffuser des messages à tous les clients en même temps.

## Logs et maintenance

- Status du service :

```bash
sudo systemctl status robot.service
```

- Logs en direct :

```bash
journalctl -u robot.service -f
```

- Pour arrêter :

```bash
sudo systemctl stop robot.service
```

- Pour redémarrer :

```bash
sudo systemctl restart robot.service
```
