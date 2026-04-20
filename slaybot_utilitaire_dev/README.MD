# slaybot_utilitaire_dev

Ce module contient des outils de simulation et de développement pour le projet SlayBot.

## Objectif

Permettre des tests logiciels sans matériel physique et vérifier le comportement WebSocket global.

## Fichiers

- `simulation.py` : simulateur de robot et serveur WebSocket.
- `generate_qr.py` : utilitaire pour générer des QR codes.
- `requirements.txt` : dépendances Python.
- `.env` / `.env.exmple` : paramètres de configuration.

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
python simulation.py
```

## Utilisation

- Simuler l’arrivée du robot.
- Tester les messages `go/X`, `order/table/X`, `clean/table/X`, `paid/table/X`.
- Déboguer l’application APK et les modules de table.

## Notes

- Ce module est essentiel pour des tests avant déploiement matériel.
- Il reproduit le protocole WebSocket du projet principal.
