#!/bin/bash
set -e

LOG_DIR="/home/hotspot/Documents/slaybot_hotspot"
mkdir -p "$LOG_DIR"

echo "-------------------------------------------------------"
echo "   SLAYBOT WIFI ROUTER PRO (ULTRA-COMPATIBLE) "
echo "-------------------------------------------------------"

echo "0: Installer / Relancer"
echo "1: Supprimer"
read -p "Choix : " CHOICE

# ---------------- WIFI DETECTION & POWER OPTIMIZATION ----------------
detect_wifi_interfaces() {
    WIFI_AP="wlan0"
    WIFI_INET="wlan1"
    
    sudo nmcli device set "$WIFI_AP" managed yes || true
    sudo nmcli device set "$WIFI_INET" managed yes || true

    echo "[INFO] Désactivation de l'économie d'énergie (Stabilité)..."
    sudo iw dev "$WIFI_AP" set power_save off || true
    sudo iw dev "$WIFI_INET" set power_save off || true
}

# ---------------- CONNECTION RASPBERRY (Internet) ----------------
connect_to_internet_source() {
    if nmcli con show --active | grep -q "raspberry"; then
        return 0
    fi

    echo "[INFO] Reconnexion à l'internet source 'raspberry'..."
    if ! nmcli con show "raspberry" >/dev/null 2>&1; then
        sudo nmcli connection add type wifi ifname "$WIFI_INET" con-name "raspberry" ssid "raspberry" -- \
            wifi-sec.key-mgmt wpa-psk wifi-sec.psk "Awawawawa"
    fi
    sudo nmcli connection up "raspberry" >/dev/null 2>&1 || true
}

# ---------------- BACKGROUND MONITORING ----------------
start_monitor() {
    (
        while true; do
            if ! nmcli -t -f active,device,ssid dev wifi | grep -q "^yes:$WIFI_INET:raspberry"; then
                connect_to_internet_source
            fi
            sleep 30
        done
    ) &
}

# ---------------- HOTSPOT (Slaybot) ----------------
install_hotspot() {
    echo "[INSTALL] Configuration du Hotspot Slaybot..."

    sudo nmcli connection delete Slaybot 2>/dev/null || true
    sudo nmcli device disconnect "$WIFI_AP" || true

    # Création avec paramètres de compatibilité moderne
    sudo nmcli con add type wifi ifname "$WIFI_AP" con-name Slaybot ssid Slaybot mode ap
    
    # ON RETIRE 'bg' : on laisse l'auto-négociation pour éviter la croix rouge sur PC
    sudo nmcli con modify Slaybot 802-11-wireless.band bg
    sudo nmcli con modify Slaybot 802-11-wireless.channel 1
    
    # SÉCURITÉ FORCÉE EN WPA2 (RSN/CCMP) pour éviter le rejet des téléphones
    sudo nmcli con modify Slaybot 802-11-wireless-security.key-mgmt wpa-psk
    sudo nmcli con modify Slaybot 802-11-wireless-security.proto rsn
    sudo nmcli con modify Slaybot 802-11-wireless-security.group ccmp
    sudo nmcli con modify Slaybot 802-11-wireless-security.pairwise ccmp
    sudo nmcli con modify Slaybot 802-11-wireless-security.psk "MHI-Hotspot"
    
    sudo nmcli con modify Slaybot ipv4.method shared
    sudo nmcli con modify Slaybot ipv4.addresses 10.42.0.1/24
    sudo nmcli con modify Slaybot connection.autoconnect yes

    sudo nmcli con up Slaybot
    
    if [ ! -d "$LOG_DIR/venv" ]; then
        python3 -m venv "$LOG_DIR/venv"
        "$LOG_DIR/venv/bin/pip" install flask psutil websockets
    fi
        
    create_robot_service
    create_web_service
    start_monitor

    echo "-------------------------------------------------------"
    echo "HOTSPOT PRÊT | SSID: Slaybot | MDP: MHI-Hotspot"
    echo "-------------------------------------------------------"
}

# ---------------- SERVICES ----------------
create_robot_service() {
    sudo bash -c "cat > /etc/systemd/system/robot.service << EOF
[Unit]
Description=Slaybot Robot Core
After=network.target NetworkManager.service

[Service]
Type=simple
User=hotspot
WorkingDirectory=$LOG_DIR
Environment=\"PYTHONUNBUFFERED=1\"
ExecStart=$LOG_DIR/venv/bin/python3 $LOG_DIR/serveur_cerveau.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"
    sudo systemctl daemon-reload
    sudo systemctl enable robot.service
    sudo systemctl restart robot.service
}

create_web_service() {
    sudo bash -c "cat > /etc/systemd/system/slaybot_web.service << EOF
[Unit]
Description=Slaybot Web Interface
After=network.target NetworkManager.service

[Service]
Type=simple
User=hotspot
WorkingDirectory=$LOG_DIR
Environment=\"PYTHONUNBUFFERED=1\"
ExecStart=$LOG_DIR/venv/bin/python3 $LOG_DIR/templates/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"
    sudo systemctl daemon-reload
    sudo systemctl enable slaybot_web.service
    sudo systemctl restart slaybot_web.service
}

clean_hotspot() {
    pkill -f "while true; do if ! nmcli" || true
    sudo systemctl stop robot.service slaybot_web.service 2>/dev/null || true
    sudo nmcli connection delete Slaybot 2>/dev/null || true
    sudo systemctl restart NetworkManager
    echo "[OK] Système réinitialisé."
}

detect_wifi_interfaces
case "$CHOICE" in
    0) install_hotspot ;;
    1) clean_hotspot ;;
    *) echo "[ERROR] Choix invalide"; exit 1 ;;
esac