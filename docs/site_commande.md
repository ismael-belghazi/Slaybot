# site_commande

Le module `site_commande` gère l'application de commande web du restaurant et la connexion avec le hotspot central.

## But du module

`site_commande` expose :

- une interface client permettant de sélectionner une table, construire un panier et envoyer une commande
- un dashboard restaurateur pour valider, annuler ou payer les commandes
- une passerelle WebSocket vers le hotspot SlayBot pour envoyer les événements opérationnels

## Architecture

- `docker-compose.yaml` : compose PostgreSQL, Flask et Cloudflare Tunnel.
- `restaurant_app/app.py` : coeur de l’application, API REST et gestion SocketIO.
- `restaurant_app/menu.json` : catalogue des produits.
- `restaurant_app/templates/` : pages HTML client et dashboard.
- `restaurant_app/static/` : JavaScript de traitement client et dashboard.

## Flux principal

1. Le client récupère le menu via `/api/menu`.
2. Il rejoint la table avec un `token` unique.
3. Les modifications de panier sont envoyées via SocketIO (`update_item`).
4. Le client confirme la commande via `send_order`.
5. Le dashboard restaurateur reçoit les commandes actives.
6. La commande peut être confirmée, annulée ou payée.
7. En cas de validation, `HotspotBridge` envoie `order/table/X` au hotspot.

## API du module

::: site_commande.restaurant_site

## Points clés

- `Order` et `TableToken` sont les tables SQL utilisées pour suivre les commandes et les tokens de session.
- `login_required` protège les routes du dashboard.
- `get_table_summary` calcule le panier et le total pour la table courante.
- `update_order_item` gère l’ajout, la modification et la suppression d’articles.
- `HotspotBridge` publie les événements `order`, `cancel` et `paid` au hotspot.
