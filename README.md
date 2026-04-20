# SlayBot

# sur pc pour avoir les requirements pour l application
pip install -r requirements.txt

# sur la raspberry 
sudo apt update
sudo apt install python3-pip
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

# etape build le project vers apk (prévoir 20, 30 minutes pour le 1er build docker essentiel)
# si c est pas deja fait 
docker compose build 
docker compose run kivy-apk buildozer init
# modfier le buildoze.spec comme vous le souhaitez
# run le build de l'application mobile
docker compose run kivy-apk buildozer android clean
# finaliser le build
docker compose run kivy-apk buildozer android debug
