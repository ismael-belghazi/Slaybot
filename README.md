# SlayBot

SlayBot est un projet de service robotisé destiné aux restaurants. Il regroupe plusieurs modules interconnectés pour gérer la commande client, l'administration, la connexion hotspot, le pilotage du robot, le tableau tactile et la simulation.

## Structure du dépôt

- `site_commande/` : application web Flask + SocketIO, dashboard restaurateur, gestion des commandes et passerelle vers le hotspot.
- `slaybot_apk/` : application mobile Android Kivy pour contrôler le robot et suivre les missions.
- `slaybot_hotspot/` : configuration Raspberry Pi pour hotspot Wi-Fi SlayBot et serveur WebSocket central.
- `slaybot_screen/` : interface tactile du robot avec visage animé et gestion des confirmations.
- `slaybot_table/` : client ESP32 pour les tables, demande le robot et affiche les états via LEDs.
- `slaybot_utilitaire_dev/` : outils de simulation et de test pour développer sans matériel réel.

## Documentation générée

Ce dépôt utilise **MkDocs** pour produire une documentation structurée et professionnelle.

### Fichiers associés

- `mkdocs.yml` : configuration du site documentation.
- `docs/` : pages de documentation utilisées par MkDocs.
- `.github/workflows/deploy-docs.yml` : workflow GitHub Actions pour déployer automatiquement la documentation sur GitHub Pages.

## Lancer la documentation localement

```bash
# Installer les dépendances de documentation depuis le venv Windows
.\.venv\Scripts\python.exe -m pip install -r docs/requirements.txt

# Servir la documentation localement depuis le venv
.\.venv\Scripts\mkdocs.exe serve
```

Ouvrez ensuite : `http://127.0.0.1:8000`

Pour générer le site statique sans le lancer :

```bash
.\.venv\Scripts\mkdocs.exe build
```

## Publier sur GitHub Pages

La publication est automatisée par le workflow GitHub Actions présent dans `.github/workflows/deploy-docs.yml`. Il génère la documentation avec MkDocs et la publie sur la branche `gh-pages`.

## Points d’attention

- Chaque module possède son README détaillé en français.
- La documentation `docs/` couvre la totalité des sous-dossiers et les principaux cas d’usage.
- Les explications sont conçues pour permettre la compréhension du fonctionnement global sans lire le code source.

## Pour commencer

1. Lisez le README du module que vous souhaitez utiliser.
2. Utilisez `mkdocs serve` pour vérifier la documentation.
3. Déployez avec GitHub Actions pour publier la documentation sur GitHub Pages.

