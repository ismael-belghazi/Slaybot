#!/bin/bash
set -e

LOG_DIR="/home/hotspot/Documents/slaybot_hotspot"
LOG_FILE="$LOG_DIR/hotspot.log"

mkdir -p "$LOG_DIR"

echo "-------------------------------------------------------"
echo "   SLAYBOT WIFI ROUTER PRO "
echo "-------------------------------------------------------"

echo "0: Installer"
echo "1: Supprimer"
echo "2: Ajouter Wi-Fi manuel"
read -p "Choix : " CHOICE

# ---------------- WIFI DETECTION ----------------
detect_wifi_interfaces() {
    WIFI_INTERFACES=($(iw dev | awk '$1=="Interface"{print $2}'))

    WIFI_AP="wlan0"
    WIFI_INET="wlan1"

    if ! iw dev wlan1 info >/dev/null 2>&1; then
        WIFI_INET=""
        WIFI_AP="wlan0"
        echo "[WARN] Mode single Wi-Fi (hotspot only)"
    fi

    echo "[INFO] AP=$WIFI_AP | INTERNET=${WIFI_INET:-NONE}"
}

# ---------------- AUTO BEST WIFI ----------------
auto_best_wifi() {
    [ -z "$WIFI_INET" ] && return

    echo "[INFO] Scan Wi-Fi..."

    sudo nmcli dev set "$WIFI_INET" managed yes

    BEST_SSID=$(nmcli -t -f SSID,SIGNAL dev wifi list ifname "$WIFI_INET" | sort -t: -k2 -nr | head -n1 | cut -d: -f1)

    if [ -z "$BEST_SSID" ]; then
        echo "[WARN] Aucun Wi-Fi détecté"
        return
    fi

    echo "[INFO] Meilleur Wi-Fi: $BEST_SSID"

    if echo "$BEST_SSID" | grep -q "raspberry"; then
        echo "[INFO] Connexion raspberry..."
        nmcli dev wifi connect "raspberry" password "Awawawawa" ifname "$WIFI_INET" || true
        return
    fi

    echo "[INFO] Connexion auto au meilleur réseau..."
    nmcli dev wifi connect "$BEST_SSID" ifname "$WIFI_INET" || true
}

# ---------------- AUTO RECONNECT ----------------
auto_reconnect() {
    (
        while true; do
            ping -c 1 8.8.8.8 >/dev/null 2>&1
            if [ $? -ne 0 ]; then
                echo "[WARN] Internet down → retry Wi-Fi"
                auto_best_wifi
            fi
            sleep 10
        done
    ) &
}

# ---------------- MANUAL WIFI ----------------
add_wifi_manual() {
    echo "-------------------------------------------------------"
    echo "AJOUT WIFI MANUEL (SAFE)"
    echo "-------------------------------------------------------"

    read -p "SSID : " SSID
    read -s -p "Mot de passe : " PASS
    echo ""

    sudo nmcli connection add type wifi ifname "$WIFI_INET" con-name "manual-$SSID" ssid "$SSID"

    sudo nmcli connection modify "manual-$SSID" wifi-sec.key-mgmt wpa-psk
    sudo nmcli connection modify "manual-$SSID" wifi-sec.psk "$PASS"
    sudo nmcli connection modify "manual-$SSID" ipv4.method auto

    sudo nmcli connection up "manual-$SSID"

    echo "[OK] Wi-Fi ajouté"
}

# ---------------- HOTSPOT ----------------
install_hotspot() {

    iw list | grep -q "AP" || {
        echo "[ERROR] AP non supporté"
        exit 1
    }

    sudo nmcli connection delete Slaybot 2>/dev/null || true

    echo "[INSTALL] Hotspot..."

    sudo nmcli con add type wifi ifname "$WIFI_AP" con-name Slaybot ssid Slaybot mode ap

    sudo nmcli con modify Slaybot 802-11-wireless.band bg
    sudo nmcli con modify Slaybot 802-11-wireless.channel 6

    sudo nmcli con modify Slaybot 802-11-wireless-security.key-mgmt wpa-psk
    sudo nmcli con modify Slaybot 802-11-wireless-security.psk "MHI-Hotspot"
    sudo nmcli con modify Slaybot 802-11-wireless-security.proto rsn
    sudo nmcli con modify Slaybot 802-11-wireless-security.pairwise ccmp
    sudo nmcli con modify Slaybot 802-11-wireless-security.group ccmp

    sudo nmcli con modify Slaybot ipv4.method shared
    sudo nmcli con modify Slaybot ipv4.addresses 10.42.0.1/24

    sudo nmcli con modify Slaybot connection.autoconnect yes

    sudo nmcli con up Slaybot

    create_robot_service

    auto_best_wifi
    auto_reconnect

    echo "-------------------------------------------------------"
    echo "HOTSPOT READY"
    echo "SSID: Slaybot"
    echo "PASSWORD: MHI-Hotspot"
    echo "IP: 10.42.0.1"
    echo "-------------------------------------------------------"
}

# ---------------- ROBOT SERVICE ----------------
create_robot_service() {
    sudo bash -c 'cat > /etc/systemd/system/robot.service << EOF
[Unit]
Description=Slaybot Robot
After=network.target NetworkManager.service

[Service]
Type=simple
User=hotspot
WorkingDirectory=/home/hotspot/Documents/slaybot_hotspot

Environment="PYTHONUNBUFFERED=1"

ExecStartPre=/bin/sleep 5
ExecStart=/home/hotspot/Documents/slaybot_hotspot/venv/bin/python3 -u /home/hotspot/Documents/slaybot_hotspot/serveur_cerveau.py

Restart=always
RestartSec=5

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF'

    sudo systemctl daemon-reload
    sudo systemctl enable robot.service
    sudo systemctl restart robot.service
}

# ---------------- CLEAN ----------------
clean_hotspot() {
    sudo nmcli connection delete Slaybot 2>/dev/null || true
    sudo nmcli device set "$WIFI_AP" managed yes || true
    sudo systemctl stop robot.service 2>/dev/null || true
    sudo systemctl daemon-reload
    sudo systemctl restart NetworkManager
}

# ---------------- MAIN ----------------
detect_wifi_interfaces

case "$CHOICE" in
    0)
        install_hotspot
        ;;
    1)
        clean_hotspot
        ;;
    2)
        detect_wifi_interfaces
        add_wifi_manual
        ;;
    *)
        echo "[ERROR] Choix invalide"
        exit 1
        ;;
esac