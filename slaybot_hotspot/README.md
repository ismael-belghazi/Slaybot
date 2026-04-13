# slaybot_hotspot

Ce module gère le hotspot Raspberry Pi SlayBot et le serveur central de message.

## Composants

- `install.sh` : installation du hotspot et des dépendances.
- `serveur_cerveau.py` : serveur WebSocket principal.
- `robot.service` : service systemd pour démarrer le serveur automatiquement.
- `requirements.txt` : dépendances Python.

## Installation

1. Copier les fichiers sur la Raspberry Pi.
2. Rendre le script exécutable :

```bash
chmod +x install.sh
```

3. Lancer l’installation :

```bash
./install.sh
```

4. Choisir l’option `0` pour créer et démarrer le hotspot.

## Configuration réseau

- SSID : `Slaybot`
- Mot de passe : `MHI-Hotspot`
- IP du hotspot : `10.42.0.1`
- Port WebSocket : `8765`

## Serveur WebSocket

Le serveur accepte les connexions des clients et diffuse les événements suivants :

- `go/X` : déplacement vers une table.
- `order/table/X` : commande cuisine.
- `clean/table/X` : demande de nettoyage.
- `ready/table/X` : commande prête.
- `cancel/table/X` : annulation.
- `paid/table/X` : paiement confirmé.

## Maintenance

- Vérifier l’état du service :

```bash
sudo systemctl status robot.service
```

- Afficher les logs :

```bash
journalctl -u robot.service -f
```

- Redémarrer le service :

```bash
sudo systemctl restart robot.service
```
