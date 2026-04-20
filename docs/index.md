# Documentation officielle de SlayBot

Bienvenue dans la documentation complète du projet **SlayBot**, un robot de service autonome pour restaurants.

##  Qu'est-ce que SlayBot ?

SlayBot est un système modulaire et interconnecté permettant :

- **Une commande web intuitive** : Interface client pour tables, dashboard restaurateur.
- **Un robot de livraison autonome** : Livraison et nettoyage automatisés des tables.
- **Une gestion centralisée** : Hotspot local Raspberry Pi avec serveur WebSocket.
- **Des interfaces spécialisées** : APK mobile, écran tactile robot, tables ESP32.
- **Un développement fluide** : Simulateur de robot pour test sans matériel.

##  Explore cette doc

### Pour comprendre le système

- **[Architecture](architecture.md)** : Diagramme complet et flux de communication.
- **[Modules](site_commande.md)** : Détail de chaque composant.

### Pour installer et utiliser

- **[Installation](installation.md)** : Setup local et déploiement complet.
- **[API Python](api.md)** : Référence complète des fonctions et classes.

### Composants

- **[site_commande](site_commande.md)** : Application web et dashboard.
- **[slaybot_apk](slaybot_apk.md)** : Application mobile de contrôle.
- **[slaybot_hotspot](slaybot_hotspot.md)** : Serveur central et hotspot.
- **[slaybot_screen](slaybot_screen.md)** : Interface tactile du robot.
- **[slaybot_table](slaybot_table.md)** : Bouton de service des tables.
- **[slaybot_utilitaire_dev](slaybot_utilitaire_dev.md)** : Simulation et test.

##  Démarrage rapide

### Installation locale

```bash
# Cloner le dépôt
git clone https://github.com/ismael-belghazi/Slaybot.git
cd Slaybot

# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\Activate.ps1

# Installer les dépendances de documentation
pip install -r docs/requirements.txt

# Lancer le serveur local
.venv\Scripts\mkdocs.exe serve
```

Le site sera accessible à `http://127.0.0.1:8000`.

## Points clés

**Modulaire** : Chaque composant fonctionne de façon indépendante.

**Temps réel** : Communication WebSocket pour synchronisation instantanée.

**Sécurisé** : Tokens de session, paiement verrouillé côté restaurateur.

**Testable** : Simulateur inclus pour valider sans matériel réel.

**Bien documenté** : Code avec docstrings + pages Markdown complètes.

## Technologie

- **Backend web** : Flask, SocketIO, PostgreSQL
- **Mobile** : Kivy (Python → APK)
- **Hotspot** : Raspberry Pi, asyncio, websockets
- **Robot** : Tkinter, WebSocket client
- **Tables** : MicroPython sur ESP32
- **Simulation** : Qt, WebSocket server
- **Documentation** : MkDocs + mkdocstrings

## Support et contribution

- Consultez le [Code de Conduite](code_of_conduct.md) pour les lignes de conduite.
- Lisez le [Guide de Contribution](contributing.md) pour contribuer.
- Voir les [Conditions d'utilisation](license.md) pour la licence.
- Consultez [SECURITY.md](https://github.com/ismael-belghazi/Slaybot/blob/main/SECURITY.md) pour les critères de sécurité.

## Documentation auto-générée

L'API Python est **entièrement documentée automatiquement** à partir du code source via [mkdocstrings](https://mkdocstrings.github.io/). Chaque page de module affiche :

- Les classes et leurs méthodes.
- Les fonctions et leurs signatures.
- Les docstrings avec exemples.
- Les annotations de type.

Les docstrings du code **apparaissent immédiatement** sur la page API sans action manuelle.

## Workflow GitHub

La documentation est **déployée automatiquement** sur GitHub Pages à chaque push vers `main`.

- Le fichier `.github/workflows/deploy-docs.yml` build et publie le site.
- **Pas d'intervention manuelle requise**.

---

**Prêt à explorer ?** Commencez par [Architecture](architecture.md) ou allez directement à [Installation](installation.md).
