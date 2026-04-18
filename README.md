# SlayBot

SlayBot est un projet de service robotisé destiné aux restaurants. Il regroupe plusieurs modules interconnectés pour gérer la commande client, l'administration, la connexion hotspot, le pilotage du robot, le tableau tactile et la simulation.

## Structure du dépôt

* `site_commande/` : application web Flask + SocketIO, dashboard restaurateur, gestion des commandes et passerelle vers le hotspot.
* `slaybot_apk/` : application mobile Android Kivy pour contrôler le robot et suivre les missions.
* `slaybot_hotspot/` : configuration Raspberry Pi pour hotspot Wi-Fi SlayBot et serveur WebSocket central.
* `slaybot_screen/` : interface tactile du robot avec visage animé et gestion des confirmations.
* `slaybot_table/` : client ESP32 pour les tables, demande le robot et affiche les états via LEDs.
* `slaybot_utilitaire_dev/` : outils de simulation et de test pour développer sans matériel réel.


## Installation et environnement Python

### Version recommandée

Python 3.11 est fortement recommandé pour éviter les problèmes de compilation avec certaines dépendances (notamment Pillow et PyQt5).


### Installation de Python

Installer Python 3.11 puis vérifier la version avec :
```bash
python --version
```

### Création d’un environnement virtuel (venv)

Créer l’environnement :

```bash
py -3.11 -m venv .venv

Activer le venv sous Windows PowerShell :

.venv\Scripts\activate
```

### Mise à jour de pip
```bash
python -m pip install --upgrade pip
```

### Installation des dépendances

Installer toutes les dépendances du projet avec :
```bash
pip install -r requirements.txt
```

## exemple de lancement

Se placer dans le dossier :
```bash
cd slaybot_utilitaire_dev
```
- Puis lancer :
```bash
python simulation.py
```


## Documentation MkDocs

### Lancer en local
```bash
.venv\Scripts\mkdocs.exe serve
```
Accès :

[http://127.0.0.1:8000](http://127.0.0.1:8000)


### Générer le site statique
```bash
.venv\Scripts\mkdocs.exe build
```

## Déploiement documentation

La documentation est automatiquement déployée via GitHub Actions sur la branche :

gh-pages


## Points importants

* Utiliser Python 3.11 uniquement (évite les erreurs de compilation des dépendances)
* Toujours recréer un venv propre en cas de conflit pip
* Éviter Python 3.13+ pour ce projet
* Mettre pip à jour avant installation


## Pour commencer

1. Installer Python 3.11
2. Créer le venv
3. Installer les dépendances
5. Lancer MkDocs si nécessaire

