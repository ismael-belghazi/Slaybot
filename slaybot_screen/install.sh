#!/bin/bash

# Couleurs pour le terminal
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}------------------------------------------------"
echo "  INSTALLATION AUTOMATIQUE SLAYBOT VISUAL"
echo -e "------------------------------------------------${NC}"

# 1. Mise à jour système et installation de Tkinter (système)
sudo apt-get update
sudo apt-get install -y python3-pip python3-tk

# 2. Installation des dépendances Python via requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installation des dépendances Python..."
    pip3 install -r requirements.txt --break-system-packages
else
    echo "Erreur : requirements.txt non trouvé !"
    exit 1
fi

# 3. Création du dossier de l'app si inexistant
APP_DIR="/home/$USER/slaybot"
mkdir -p $APP_DIR

# 4. Configuration du service Systemd pour l'Auto-run
SERVICE_FILE="/etc/systemd/system/slaybot_face.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=SlayBot Face Interface
After=network.target

[Service]
ExecStart=/usr/bin/python3 $APP_DIR/face.py
WorkingDirectory=$APP_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$USER
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/$USER/.Xauthority

[Install]
WantedBy=graphical.target
EOF

# 5. Activation du service
sudo systemctl daemon-reload
sudo systemctl enable slaybot_face.service

echo -e "${GREEN}------------------------------------------------"
echo "INSTALLATION RÉUSSIE !"
echo "Vérifie que face.py est bien dans $APP_DIR"
echo "Redémarre pour tester : sudo reboot"
echo -e "------------------------------------------------${NC}"