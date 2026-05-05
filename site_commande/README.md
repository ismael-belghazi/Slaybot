# site_commande

Cette section du projet gère l'interface web de commande pour restaurant, permettant aux clients de passer des commandes via un site web, et aux restaurateurs de gérer ces commandes en temps réel. Elle inclut la gestion des sessions de table, la validation des tokens, et la communication avec le hotspot SlayBot pour la préparation des commandes.

## Composants

- `docker-compose.yaml` : Orchestration des services (PostgreSQL, application Flask, tunnel Cloudflare).
- `restaurant_site/app.py` : Cœur de l'application Flask avec SocketIO pour communications temps réel.
- `restaurant_site/menu.json` : Catalogue des plats, entrées, desserts et boissons avec prix et images.
- `restaurant_site/templates/` : Pages HTML (client.html, dashboard.html, login.html).
- `restaurant_site/static/` : Fichiers CSS, JS et images pour l'interface utilisateur.
- `install_docker_stack.sh` : Script d'installation pour déployer la stack Docker.

## Fonctionnalités principales

- **Gestion des commandes** : Ajout, modification et suppression d'articles dans le panier.
- **Authentification restaurateur** : Connexion sécurisée pour accéder au dashboard.
- **Temps réel** : Mises à jour instantanées via WebSocket pour clients et dashboard.
- **Gestion des tokens** : Système de tokens par table pour sécuriser les sessions.
- **Intégration hotspot** : Communication avec le serveur cerveau du hotspot pour notifications (commande, annulation, paiement).
- **Base de données** : Stockage des commandes et tokens avec PostgreSQL.

## Classes et fonctions importantes

### Modèles de base de données
- `Order` : Représente une commande avec numéro de table, plats (sous forme de chaîne), statut, token et paiement.
- `TableToken` : Gère les tokens de session actifs par table.

### Classes utilitaires
- `HotspotBridge` : Pont WebSocket pour communiquer avec le serveur hotspot (connexion, envoi de messages pour commandes, annulations, paiements).

### Fonctions clés
- `get_table_summary(table_number)` : Calcule le résumé des commandes non payées pour une table (articles et total).
- `validate_token(table, token)` : Vérifie si un token est valide pour une table.
- `update_order_item(table, token, item, delta)` : Met à jour la quantité d'un article dans une commande.
- `serialize_order(order)` : Sérialise une commande pour l'affichage.

### Routes Flask
- `/` : Redirection vers login ou dashboard selon session.
- `/login` : Page de connexion pour restaurateurs.
- `/dashboard` : Interface de gestion des commandes.
- `/client` : Interface client pour passer commande (nécessite paramètres `table` et `token`).
- `/api/menu` : API pour récupérer le menu au format JSON.

### Événements SocketIO
- `join_table` : Rejoindre la salle d'une table avec validation du token.
- `update_item` : Mettre à jour un article dans le panier.
- `send_order` : Envoyer la commande finale.
- `confirm_order` : Valider la commande côté restaurateur (envoie au hotspot).
- `cancel_order` : Annuler une commande.
- `pay_order` : Marquer comme payé et fermer la session.

## Exemples d'utilisation

### Flux client
1. Accès via URL avec `?table=5&token=abc123`.
2. Sélection d'articles dans le menu.
3. Validation de la commande, qui est stockée en base.
4. Réception de confirmations en temps réel.

### Flux restaurateur
1. Connexion au dashboard avec identifiants (par défaut admin/admin).
2. Visualisation des commandes en attente.
3. Validation d'une commande : statut passe à 'PRET', notification envoyée au hotspot.
4. Gestion des paiements : suppression des commandes, invalidation des tokens.

### Communication avec hotspot
- Lors de validation : `HotspotBridge.send_order(table_number)`
- Lors d'annulation : `HotspotBridge.send_cancel(table_number)`
- Lors de paiement : `HotspotBridge.send_payment(table_number)`

## Architecture technique

- **Backend** : Flask avec SQLAlchemy pour ORM, SocketIO pour WebSocket.
- **Frontend** : HTML/CSS/JS vanilla avec SocketIO client.
- **Base de données** : PostgreSQL avec tables `orders` et `table_tokens`.
- **Déploiement** : Docker Compose pour conteneurisation, tunnel Cloudflare pour accès externe.
- **Sécurité** : Authentification par session Flask, validation de tokens par table.

## Déploiement local

1. Copier `.env.exemple` en `.env`.
2. Modifier les variables nécessaires : base de données, identifiants et `HOTSPOT_WS_URL`.
3. Lancer :

```bash
docker compose up -d --build
```

4. Accéder à `http://localhost:5000`.

## Bonnes pratiques

- Vérifier que le hotspot SlayBot est accessible sur `HOTSPOT_WS_URL`.
- Ne pas exposer le dashboard sans protection adéquate.
- Utiliser les tokens de table pour éviter les accès non autorisés.

