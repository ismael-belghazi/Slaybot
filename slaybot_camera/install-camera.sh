#!/bin/bash

# ==============================================================================
# SlayBot Camera - Script d'installation automatisé
# ==============================================================================

set -euo pipefail

# Configuration
APP_NAME="slaybot_camera"
PORT=5001
VENV_DIR=".venv"

# Fonctions utilitaires pour l'affichage
info() { echo -e "\033[1;34m[INFO]\033[0m $1"; }
success() { echo -e "\033[1;32m[OK]\033[0m $1"; }
error() { echo -e "\033[1;31m[ERREUR]\033[0m $1"; exit 1; }

[[ $EUID -ne 0 ]] && error "Ce script doit être exécuté avec sudo."

USER_NAME=${SUDO_USER:-$USER}
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
INPUT_ARG=${1:-0} 
PORT=5001

if [[ "$INPUT_ARG" == "1" ]]; then
    info "Désinstallation complète de SlayBot Camera (Mode 1)..."
    systemctl stop "${APP_NAME}.service" || true
    systemctl disable "${APP_NAME}.service" || true
    rm -f "/etc/systemd/system/${APP_NAME}.service"
    systemctl daemon-reload
    rm -rf "${SCRIPT_DIR}/${VENV_DIR}"
    success "Désinstallation terminée."
    exit 0
fi

info "Installation de SlayBot Camera (Mode 0)..."
systemctl stop "${APP_NAME}.service" 2>/dev/null || true

info "Installation des dépendances système..."
apt-get update -qq && apt-get install -y python3-pip python3-venv v4l-utils libopenblas-dev libgl1 > /dev/null

info "Configuration de l'environnement Python..."
cd "${SCRIPT_DIR}"
sudo -u "$USER_NAME" python3 -m venv "$VENV_DIR"
sudo -u "$USER_NAME" "$VENV_DIR/bin/pip" install --upgrade pip -q
sudo -u "$USER_NAME" "$VENV_DIR/bin/pip" install flask opencv-python-headless numpy > /dev/null

info "Configuration du service Systemd..."
cat <<EOF > "/etc/systemd/system/${APP_NAME}.service"
[Unit]
Description=SlayBot Camera Streaming Service
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=${SCRIPT_DIR}
Environment="CAMERA_INDEX=0"
Environment="CAMERA_PORT=$PORT"
ExecStart=${SCRIPT_DIR}/${VENV_DIR}/bin/python3 main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "${APP_NAME}.service"
systemctl start "${APP_NAME}.service"

success "SlayBot Camera est installé et démarré !"
info "-------------------------------------------------------"
info "  - Interface Live  : http://$(hostname -I | cut -d' ' -f1):$PORT"
info "  - API Status      : http://$(hostname -I | cut -d' ' -f1):$PORT/status"
info "  - Désinstaller    : sudo ./install-camera.sh 1"
info "-------------------------------------------------------"