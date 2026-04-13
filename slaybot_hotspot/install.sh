#!/bin/bash
set -e

LOG_DIR="/home/hotspot/Documents/slaybot_hotspot"
LOG_FILE="$LOG_DIR/hotspot.log"
WIFI_IFACE="wlan0"

mkdir -p "$LOG_DIR"

echo "-------------------------------------------------------"
echo "   GESTION DU HOTSPOT SLAYBOT (VERSION CORRIGEE)"
echo "-------------------------------------------------------"

read -p "0: Installer/lancer hotspot | 1: Supprimer hotspot : " CHOICE

# ---------------- INTERNET CHECK ----------------
check_internet() {
    echo "[INFO] Vérification de l'accès Internet..."

    sudo nmcli connection modify "$WIFI_IFACE" ipv4.ignore-auto-dns yes || true
    sudo nmcli connection modify "$WIFI_IFACE" ipv4.dns "8.8.8.8 1.1.1.1" || true
    sudo nmcli connection up "$WIFI_IFACE" || true

    # Vérification de la connexion à Internet
    if ! ping -c 2 8.8.8.8 >/dev/null 2>&1; then
        echo "[ERROR] Pas d'accès Internet"
        exit 1
    fi
}

# ---------------- APT ----------------
update_packages() {
    echo "[INFO] Mise à jour du système..."
    sudo apt-get update -y
    sudo apt-get upgrade -y
}

# ---------------- PYTHON (SAFE MODE) ----------------
install_python() {
    echo "[INSTALL] Installation de Python (mode sécurisé)..."

    # Installation des paquets Python de base
    sudo apt-get install -y python3 python3-venv python3-pip python3-websockets python3-serial

    # Définition de la variable PYTHON_BIN
    PYTHON_BIN=python3
}

# ---------------- DEPENDENCIES ----------------
create_virtualenv() {
    # Créer l'environnement virtuel si il n'existe pas
    if [ ! -d "$LOG_DIR/venv" ]; then
        echo "[INFO] Création de l'environnement virtuel..."
        $PYTHON_BIN -m venv "$LOG_DIR/venv"
    else
        echo "[INFO] L'environnement virtuel existe déjà."
    fi
}

install_dependencies() {
    echo "[INSTALL] Installation des dépendances Python..."

    # Créer l'environnement virtuel si nécessaire
    create_virtualenv

    # Activation de l'environnement virtuel
    source "$LOG_DIR/venv/bin/activate"

    # Mise à jour de pip, setuptools et wheel
    python3 -m pip install --upgrade pip setuptools wheel

    # Installation de websockets et pyserial
    pip install websockets pyserial

    # Désactivation de l'environnement virtuel
    deactivate
}

# ---------------- CLEAN HOTSPOT ----------------
clean_hotspot() {
    echo "[CLEAN] Suppression du hotspot..."

    # Suppression de la connexion "Slaybot" si elle existe
    sudo nmcli connection delete Slaybot 2>/dev/null || true

    # Remettre l'interface wifi en mode "géré"
    sudo nmcli device set "$WIFI_IFACE" managed yes || true

    # Désactivation du service robot.service si nécessaire
    sudo systemctl stop robot.service 2>/dev/null || true
    sudo systemctl disable robot.service 2>/dev/null || true
    sudo rm -f /etc/systemd/system/robot.service || true

    # Rechargement des services système
    sudo systemctl daemon-reload
    sudo systemctl restart NetworkManager

    echo "[CLEAN] Hotspot supprimé et Wi-Fi rétabli."
}

# ---------------- HOTSPOT INSTALL ----------------
install_hotspot() {
    # Capture du log dans un fichier
    exec > >(tee -a "$LOG_FILE") 2>&1

    # Vérification du mode AP supporté par la carte wifi
    echo "[INSTALL] Vérification du support du mode AP..."
    iw list | grep -q "AP" || {
        echo "[ERROR] Le mode AP n'est pas supporté par votre carte Wi-Fi."
        exit 1
    }

    # Installation de Python et des dépendances
    install_python
    install_dependencies

    # Nettoyage du hotspot précédent
    clean_hotspot

    # Création du hotspot Slaybot
    echo "[INSTALL] Création du hotspot Slaybot..."
    sudo nmcli con add type wifi ifname "$WIFI_IFACE" con-name Slaybot ssid Slaybot mode ap
    sudo nmcli con modify Slaybot 802-11-wireless.band bg
    sudo nmcli con modify Slaybot 802-11-wireless.channel 6
    sudo nmcli con modify Slaybot wifi-sec.key-mgmt wpa-psk
    sudo nmcli con modify Slaybot wifi-sec.psk "MHI-Hotspot"
    sudo nmcli con modify Slaybot ipv4.method shared
    sudo nmcli con modify Slaybot ipv4.addresses 10.42.0.1/24

    # Passer l'interface Wi-Fi en mode "non géré" et démarrer le hotspot
    sudo nmcli device set "$WIFI_IFACE" managed no
    sudo nmcli con up Slaybot || echo "[WARN] Le démarrage du hotspot a échoué."

    # Affichage des informations de connexion
    echo "-------------------------------------------------------"
    echo "HOTSPOT PRÊT"
    echo "SSID: Slaybot"
    echo "IP: 10.42.0.1"
    echo "-------------------------------------------------------"
}

# ---------------- MAIN ----------------
# Exécution en fonction du choix de l'utilisateur
if [ "$CHOICE" == "0" ]; then
    check_internet
    update_packages
    install_hotspot

elif [ "$CHOICE" == "1" ]; then
    clean_hotspot

else
    echo "[ERROR] Choix invalide. L'installation a échoué."
    exit 1
fi