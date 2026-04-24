# site_commande

Cette section du projet gère l’interface web de commande, les sessions de table, la validation restaurateur et la communication vers le hotspot SlayBot.

## Composants

- `docker-compose.yaml` : instancie PostgreSQL, l’application Flask et le tunnel Cloudflare.
- `restaurant_app/app.py` : coeur de l’application.
- `restaurant_app/menu.json` : catalogue des plats et des boissons.
- `restaurant_app/templates/` : pages HTML pour le client et le dashboard.
- `restaurant_app/static/` : JavaScript client pour SocketIO et mises à jour en temps réel.

## Fonctionnement

### Flux client

1. Le client arrive sur la page web de commande.
2. Il accède à une table via un paramètre `table` et un `token` de session.
3. Le token est vérifié avec `TableToken` et activé pour la table.
4. Le client peut ajouter, modifier ou supprimer des éléments de commande.
5. La commande est envoyée au serveur lorsque le client valide.

### Flux restaurateur

1. Le restaurateur se connecte à `dashboard` avec des identifiants.
2. Il voit les commandes en cours et les tables actives.
3. Il valide, annule ou marque comme payée chaque commande.
4. Seule la validation depuis le dashboard déclenche l’envoi au hotspot.

### Gestion des tokens

- Les tokens sont générés et stockés par table.
- Un token actif permet au client de rejoindre la salle SocketIO de sa table.
- Après paiement, tous les tokens de la table sont invalidés.

## Architecture technique

### Base de données

- `Order` : table des commandes avec `table_number`, `plats`, `status`, `token` et `paid`.
- `TableToken` : table des tokens de session par table.

### WebSocket

- `join_table` : le client rejoint sa salle dédiée.
- `join_dashboard` : le dashboard rejoint la salle `dashboard`.
- `update_item` : mise à jour du panier.
- `send_order` : envoi de la commande finale.
- `confirm_order` : validation de la commande côté restaurateur.
- `pay_order` : paiement et fermeture de la session.

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

