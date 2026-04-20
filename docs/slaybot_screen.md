# slaybot_screen

Le module `slaybot_screen` fournit l’interface tactile embarquée du robot, avec visage animé et contrôle de mission.

## But du module

`slaybot_screen` transforme les messages du hotspot en statut visuel et actions :

- affichage d’un visage animé selon l’état
- confirmation de livraison
- arrêt d’urgence
- reconnexion automatique au serveur SlayBot

## Composants

- `face.py` : logique de rendu Tkinter et client WebSocket.
- `requirements.txt` : dépendances Python.
- `install.sh` : installation sur Raspberry Pi.

## API du module

::: slaybot_screen.face

## Fonctionnement

- `SlayBotVisual.listen()` se connecte au serveur WebSocket.
- Les messages suivants changent l’interface :
  - `deplacement table X` -> affiche état "EN ROUTE"
  - `arrived/table` -> affiche bouton de confirmation
  - `arrived/bar` -> retourne au statut prêt
- `send_confirm()` envoie `status/received` au hotspot.
- `send_emergency()` envoie `status/emergency_stop`.

## Mise en place

1. Copier le dossier sur la Raspberry Pi.
2. Ajuster `SERVER_IP` si nécessaire.
3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

4. Lancer :

```bash
python face.py
```
