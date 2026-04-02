#!/bin/bash

# Arrêter le script en cas d'erreur
set -e

echo "-------------------------------------------------------"
echo "   DÉBUT DE L'INSTALLATION DU CERVEAU SLAYBOT"
echo "-------------------------------------------------------"

# 1. Mise à jour du système (Optionnel si pas d'Internet)
echo "[1/6] Mise à jour du système..."
sudo apt update || echo "Serveurs injoignables, on saute la mise à jour."

# 2. Installation des dépendances
echo "[2/6] Vérification des outils..."
sudo apt install -y network-manager python3-pip python3-venv || echo "Échec install apt, on continue..."

# 3. Configuration du Hotspot Wi-Fi (CORRIGÉ POUR DEBIAN TRIXIE)
echo "[3/6] Configuration du Hotspot Wi-Fi : Slaybot..."
# Nettoyage
sudo nmcli connection down Slaybot || true
sudo nmcli connection delete Slaybot || true

# Création avec le mode 'ap' (Access Point)
sudo nmcli con add type wifi ifname wlan0 con-name Slaybot autoconnect yes ssid Slaybot mode ap
sudo nmcli con modify Slaybot 802-11-wireless.security-proto rsn
sudo nmcli con modify Slaybot 802-11-wireless-security.key-mgmt wpa-psk
sudo nmcli con modify Slaybot 802-11-wireless-security.psk "MHI-Hotspot"
sudo nmcli con modify Slaybot ipv4.addresses 10.42.0.1/24 ipv4.method shared

echo "Démarrage du Wi-Fi..."
sudo nmcli con up Slaybot

# 4. Préparation de l'environnement Python
echo "[4/6] Création du VENV..."
cd /home/admin/Documents/hotspot
rm -rf venv
python3 -m venv venv
source venv/bin/activate
echo "Installation des librairies..."
# On utilise les versions déjà en cache si pas d'Internet
pip install websockets pyserial --trusted-host pypi.org --trusted-host files.pythonhosted.org || echo "Attention : Bibliothèques non installées (Pas d'internet ?)"

# 5. Configuration du service Systemd
echo "[5/6] Configuration du lancement automatique..."
if [ -f "/home/admin/Documents/hotspot/robot.service" ]; then
    sudo cp /home/admin/Documents/hotspot/robot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable robot.service
    sudo systemctl restart robot.service
    echo "Service activé !"
else
    echo "ERREUR : robot.service introuvable dans /home/admin/Documents/hotspot/"
fi

# 6. Finalisation
echo "-------------------------------------------------------"
echo "   INSTALLATION TERMINÉE !"
echo "-------------------------------------------------------"
echo "Connecte-toi au Wi-Fi : Slaybot"
echo "IP du Cerveau : 10.42.0.1"
echo "-------------------------------------------------------"