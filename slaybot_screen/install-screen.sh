#!/bin/bash

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# --- CONFIG ---
APP_DIR="/home/$USER/slaybot"
VENV_DIR="$APP_DIR/venv"
SERVICE_FILE="/etc/systemd/system/slaybot_face.service"
SRC_DIR="$(pwd)"
PYTHON_FILE="face.py"

echo -e "${GREEN}------------------------------------------------"
echo "   SLAYBOT VISUAL AUTOMATION SCRIPT INSTALLER"
echo -e "------------------------------------------------${NC}"

CHOICE=$1

# =========================
# INSTALLATION
# =========================
if [ "$CHOICE" == "1" ]; then
    echo -e "${GREEN}=== DÉBUT DE L'INSTALLATION ===${NC}"

    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-pip python3-tk \
        network-manager x11-xserver-utils unclutter

    mkdir -p "$APP_DIR"

    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}Configuration de l'environnement Python...${NC}"
        python3 -m venv "$VENV_DIR"
    fi

    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install websockets

    if [ -f "$SRC_DIR/$PYTHON_FILE" ]; then
        cp "$SRC_DIR/$PYTHON_FILE" "$APP_DIR/face.py"
        chmod +x "$APP_DIR/face.py"
    else
        echo -e "${RED}Erreur : $PYTHON_FILE introuvable dans le dossier actuel.${NC}"
        exit 1
    fi

    # =========================
    # SERVICE SYSTEMD (FACE UNIQUEMENT)
    # =========================
    
    echo -e "${YELLOW}Installation du service Face...${NC}"
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=SlayBot Face Interface
After=graphical.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/$USER/.Xauthority
ExecStart=$VENV_DIR/bin/python3 $APP_DIR/face.py
Restart=always
RestartSec=5

[Install]
WantedBy=graphical.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable slaybot_face.service
    sudo systemctl restart slaybot_face.service

    echo -e "${GREEN}=== INSTALLATION TERMINÉE ===${NC}"

# =========================
# DÉSINSTALLATION
# =========================
elif [ "$CHOICE" == "0" ]; then
    echo -e "${YELLOW}Désinstallation...${NC}"
    sudo systemctl stop slaybot_face.service 2>/dev/null
    sudo systemctl disable slaybot_face.service 2>/dev/null
    sudo rm -f "$SERVICE_FILE"
    
    # Nettoyage de l'ancien script wifi s'il existait
    sudo systemctl stop slaybot_wifi.service 2>/dev/null
    sudo systemctl disable slaybot_wifi.service 2>/dev/null
    sudo rm -f "/etc/systemd/system/slaybot_wifi.service"
    rm -f "$APP_DIR/wifi_manager.sh"

    sudo systemctl daemon-reload
    echo -e "${GREEN}Services et fichiers supprimés.${NC}"

else
    echo -e "${YELLOW}Usage :${NC} $0 1 (Installer) ou $0 0 (Désinstaller)"
fi