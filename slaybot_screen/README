# Ce projet contient l'interface graphique du robot SlayBot. Il s'exécute sur une Raspberry Pi avec écran et communique via WebSockets avec le serveur de contrôle des moteurs.

### Fonctionnalités

- Visage Dynamique : Dessins vectoriels changeant selon l'état du robot (Heureux, Étonné, Erreur).

- Bouton Arrêt d'Urgence : Permet de stopper le robot directement depuis l'écran tactile.

- Confirmation de Réception : Un bouton vert apparaît uniquement quand le robot est arrivé à la table du client.

- Auto-Run : Le script se lance automatiquement au démarrage grâce à un service système (systemd).

- Installation Automatisée : Un script bash gère l'installation des dépendances et la configuration.

### Structure du projet

- face.py : Code principal de l'interface (Tkinter + WebSockets).

- requirements.txt : Liste des dépendances Python nécessaires.
 
- install.sh : Script d'installation et de configuration de l'auto-run.

### Installation
- Déposez les fichiers dans le dossier /home/pi/slaybot sur la Raspberry Pi.

- Ouvrez un terminal dans ce dossier.

- Rendez le script d'installation exécutable :
```bash
chmod +x install.sh
```
- Lancez l'installation :
```bash
./install.sh
```

- Redémarrez l'appareil :
```bash
sudo reboot
``` 

### Configuration Réseau
- L'adresse IP du serveur maître doit être renseignée dans le fichier face.py à la ligne suivante :

>SERVER_IP = "10.42.0.1"

## Communication (Protocole WebSocket)
- Messages reçus par l'écran (Serveur vers Écran) :
>deplacement table X : Le visage devient jaune (livraison en cours).

- arrived/table : 
>Le visage devient heureux et affiche le bouton de confirmation vert.

- arrived/bar : 
> Le visage revient à l'état normal (prêt au bar).

### Messages envoyés par l'écran (Écran vers Serveur) :
- status/received : 
> Envoyé lors du clic sur le bouton vert de confirmation.

- status/emergency_stop : 
> Envoyé lors du clic sur le bouton rouge STOP.

### Commandes utiles
- Vérifier l'état du service auto-run :
```bash
sudo systemctl status slaybot_face.service
```

- Arrêter l'interface :
```bash
sudo systemctl stop slaybot_face.service
```

- Relancer l'interface :
```bash
sudo systemctl start slaybot_face.service
```

SlayBot Project - 2026 ©