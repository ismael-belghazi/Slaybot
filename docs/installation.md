# Installation 

Ce guide couvre l'installation locale complète de SlayBot 

## Prérequis

### Matériel et outils globaux

- Git et un compte GitHub pour la gestion de version.
- Python 3.10+ pour les modules backend.
- Docker et Docker Compose pour `site_commande` et la compilation APK.
- VS Code, PyCharm ou tout éditeur Python compatible.
- Buildozer pour la génération d'APK Android (via Docker).

### Environnement local (développement)

- Un environnement virtuel Python isolé (`.venv`).
- Les dépendances listées dans chaque `requirements.txt` de module.

## Installation locale rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/ismael-belghazi/Slaybot.git
cd Slaybot
```

### 2. Créer et activer l'environnement virtuel

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
```


## Installation des modules

### `site_commande` (application web)

```bash
cd site_commande
pip install -r requirements.txt
docker compose up -d --build  # Lance la stack complète
```

Accessible sur `http://localhost:5000`.

### `slaybot_apk` (application mobile)

Requiert Buildozer via Docker :

```bash
cd slaybot_apk
docker compose run --rm kivy-apk buildozer android debug
```

L'APK générée sera dans `bin/`.

### `slaybot_hotspot` (Raspberry Pi)

Sur la Raspberry Pi :

```bash
cd slaybot_hotspot
chmod +x install.sh
./install.sh
```

Choisissez l'option `0` pour activer le hotspot.

### `slaybot_screen` (interface robot)

```bash
cd slaybot_screen
pip install -r requirements.txt
python face.py
```

Vérifiez que `SERVER_IP` pointe vers le hotspot.

### `slaybot_table` (table ESP32)

1. Flashez l'ESP32 avec MicroPython.
2. Copiez `table_esp32_code_generique.py` en tant que `main.py`.
3. Configurez les variables (SSID, TABLE_ID).
4. Redémarrez l'appareil.

### `slaybot_utilitaire_dev` (simulation)

```bash
cd slaybot_utilitaire_dev
pip install -r requirements.txt
python simulation.py
```

Le simulateur démarre un serveur WebSocket local et affiche la position du robot.

## Commandes utiles
### Gestion Git

```bash
# Ajouter tous les fichiers modifiés
git add .

# Commiter avec un message descriptif
git commit -m "Amélioration documentation SlayBot"

# Pousser vers le dépôt distant
git push origin main

# Voir l'historique

git log --oneline -n 10
```
## Dépannage

### Docker : compose not found

Installez Docker Desktop pour Windows ou atualisez vers une version récente de Docker.

### APK : erreur de build

Vérifiez que :
- Buildozer est bien dans le conteneur Docker.
- La version de Kivy dans `buildozer.spec` est compatible.
- Les permissions d'utilisation Android sont correctes.

## Prochaines étapes

- Consultez the [Architecture](architecture.md) pour comprendre le flux global.
- Lisez les pages de module pour des détails sur chaque composant.
- Explorez la page [API](api.md) pour les références de fonction.
- Testez le simulateur dans `slaybot_utilitaire_dev` pour valider le protocole.
