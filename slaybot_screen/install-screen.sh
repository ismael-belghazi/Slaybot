#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# --- CONFIGURATION ---
APP_DIR="/home/$USER/slaybot"
VENV_DIR="$APP_DIR/venv"
SERVICE_FILE="/etc/systemd/system/slaybot_face.service"
SRC_DIR="$(pwd)"
PYTHON_FILE="face.py" 

WIFI_SSID="Slaybot"
WIFI_PASS="MHI-Hotspot"

echo -e "${GREEN}------------------------------------------------"
echo "   SLAYBOT VISUAL AUTOMATION SCRIPT"
echo -e "------------------------------------------------${NC}"

CHOICE=$1

if [ "$CHOICE" == "1" ]; then
    echo -e "${GREEN}=== INSTALLATION ===${NC}"

    # 1. Mise à jour et outils
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-tk network-manager x11-xserver-utils

    # 2. Dossiers
    mkdir -p "$APP_DIR"

    # 3. Environnement virtuel
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
    fi
    source "$VENV_DIR/bin/activate"

    # 4. Dépendances
    pip install --upgrade pip
    pip install websockets

    # 5. Copie du fichier Python
    if [ -f "$SRC_DIR/$PYTHON_FILE" ]; then
        cp "$SRC_DIR/$PYTHON_FILE" "$APP_DIR/face.py"
        chmod +x "$APP_DIR/face.py"
        echo "Fichier copié dans $APP_DIR/face.py"
    else
        echo -e "${RED}Erreur : $PYTHON_FILE introuvable dans $SRC_DIR.${NC}"
        exit 1
    fi

    # 6. Wi-Fi (NMCLI)
    echo -e "${GREEN}Tentative de connexion au Wi-Fi $WIFI_SSID...${NC}"
    # On oublie l'ancienne connexion pour éviter les conflits de mdp
    sudo nmcli connection delete "$WIFI_SSID" 2>/dev/null
    sudo nmcli device wifi connect "$WIFI_SSID" password "$WIFI_PASS"

    # 7. Création du service systemd
    sudo bash -c "cat > $SERVICE_FILE" <<EOF
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
# On force l'affichage et on lance Python
ExecStartPre=/usr/bin/xhost +SI:localuser:$USER
ExecStart=$VENV_DIR/bin/python3 $APP_DIR/face.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
EOF

    # 8. Activation
    sudo systemctl daemon-reload
    sudo systemctl enable slaybot_face.service
    sudo systemctl start slaybot_face.service

    echo -e "${GREEN}Installation terminée !${NC}"
    echo "Si l'écran ne s'affiche pas, tape: 'export DISPLAY=:0 && xhost +'"

elif [ "$CHOICE" == "0" ]; then
    echo -e "${RED}=== DESINSTALLATION ===${NC}"
    sudo systemctl stop slaybot_face.service
    sudo systemctl disable slaybot_face.service
    sudo rm -f "$SERVICE_FILE"
    sudo systemctl daemon-reload
    echo "Service supprimé."
else
    echo "Usage : $0 1 (installer) ou $0 0 (désinstaller)"
fi