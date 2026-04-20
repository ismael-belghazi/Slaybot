# Installation et déploiement

Ce guide présente les étapes d'installation pour chaque module ainsi que le déploiement de la documentation sur GitHub Pages.

## Prérequis

- Git et un compte GitHub.
- Python 3.10+ pour les modules backend et simulation.
- Docker et Docker Compose pour `site_commande` et la compilation APK.
- Buildozer pour la génération d'APK Android (via Docker dans ce projet).

## Génération de la documentation

Ce projet utilise MkDocs pour générer un site de documentation statique.

### Installer MkDocs

Dans un environnement virtuel Python Windows :

```bash
.\.venv\Scripts\python.exe -m pip install -r docs/requirements.txt
```

`docs/requirements.txt` contient MkDocs, le thème Material et les extensions de documentation automatique.

### Générer le site localement

```bash
.\.venv\Scripts\mkdocs.exe serve
```

Le site sera accessible sur `http://127.0.0.1:8000`.

### Générer les fichiers statiques

```bash
.\.venv\Scripts\mkdocs.exe build --clean
```

Les pages sont générées dans le dossier `site/`.

## Déploiement GitHub Pages

La publication sur GitHub Pages est automatisée avec un workflow GitHub Actions.

1. Pousser le dépôt vers GitHub.
2. Activer GitHub Pages sur la branche `gh-pages`.
3. Le workflow `.github/workflows/deploy-docs.yml` construira la documentation et la publiera automatiquement.
## Dépannage

### MkDocs : "plugin mkdocstrings not installed"

Solution :

```bash
.venv\Scripts\python.exe -m pip install -r docs/requirements.txt
```

### MkDocs : modules Python non trouvés

Vérifiez que le dossier racine est ajouté au PYTHONPATH dans `mkdocs.yml` :

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          setup_commands:
            - "import sys, os; sys.path.insert(0, os.path.abspath('.'))"
```

## Commandes utiles

```bash
git add .
git commit -m "Documentation complète SlayBot"
git push origin main
```

Si vous souhaitez forcer une reconstruction locale :

```bash
mkdocs build --clean
```
