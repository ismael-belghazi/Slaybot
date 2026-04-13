# slaybot_screen

Le module `slaybot_screen` fournit l’interface graphique embarquée du robot, tournée vers l’affichage d’état et la confirmation de livraison.

## Fichiers

- `face.py` : application principale.
- `requirements.txt` : dépendances Python.
- `install.sh` : script d’installation et de configuration.

## Fonctionnalités

- Visage animé selon l’état du robot.
- Bouton vert de confirmation visible après arrivée à la table.
- Bouton rouge d’arrêt d’urgence.
- Reconnexion automatique à chaque perte de connexion.

## Connexion

Le module se connecte à l’adresse WebSocket :

```python
ws://10.42.0.1:8765
```

### Messages reçus

- `deplacement table X` : passage à l’état livraison.
- `arrived/table` : activation du bouton de confirmation.
- `arrived/bar` : retour en état prêt.

### Messages envoyés

- `status/received` : confirmation de livraison.
- `status/emergency_stop` : arrêt d’urgence.

## Lancement

1. Copier les fichiers sur la Raspberry Pi.
2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Exécuter :

```bash
python face.py
```

## Notes

- Vérifier la variable `SERVER_IP` si le hotspot change d’adresse.
- Le module doit pouvoir accéder au hotspot local pour rester connecté.
