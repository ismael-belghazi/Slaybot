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

    KNOWN_SSIDS=("raspberry")  # Liste des SSID connus
    SSID_TO_CONNECT=""

    for SSID in $(nmcli -t -f SSID dev wifi list ifname "$WIFI_INET" | grep -v "Slaybot"); do
        if [[ " ${KNOWN_SSIDS[@]} " =~ " ${SSID} " ]]; then
            SSID_TO_CONNECT="$SSID"
            break
        fi
    done

    if [ -z "$SSID_TO_CONNECT" ]; then
        echo "[INFO] Aucun réseau connu trouvé, recherche du meilleur réseau alternatif..."
        BEST_SSID=$(nmcli -t -f SSID,SIGNAL dev wifi list ifname "$WIFI_INET" | sort -t: -k2 -nr | head -n1 | cut -d: -f1)
        SSID_TO_CONNECT="$BEST_SSID"
    fi

    if [ -z "$SSID_TO_CONNECT" ]; then
        echo "[WARN] Aucun Wi-Fi détecté"
        return
    fi

    echo "[INFO] Connexion au réseau : $SSID_TO_CONNECT"

    if echo "$SSID_TO_CONNECT" | grep -q "raspberry"; then
        echo "[INFO] Connexion à raspberry..."
        nmcli dev wifi connect "raspberry" password "Awawawawa" ifname "$WIFI_INET" \
            wifi-sec.key-mgmt wpa-psk \
            wifi-sec.proto rsn \
            wifi-sec.pairwise ccmp \
            wifi-sec.group ccmp || {
                echo "[ERROR] Échec de la connexion à raspberry, tentative de reconnexion."
                sudo nmcli connection delete "raspberry" 2>/dev/null || true
                sudo nmcli dev wifi connect "raspberry" password "Awawawawa" ifname "$WIFI_INET" \
                    wifi-sec.key-mgmt wpa-psk \
                    wifi-sec.proto rsn \
                    wifi-sec.pairwise ccmp \
                    wifi-sec.group ccmp || true
            }
    else
        echo "[INFO] Connexion au meilleur réseau trouvé : $SSID_TO_CONNECT"
        nmcli dev wifi connect "$SSID_TO_CONNECT" ifname "$WIFI_INET" || true
    fi
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
            sleep 30  # Augmenter le temps entre les tentatives de reconnexion
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

    # Forcer l'utilisation de la bande 2.4GHz (bande bg)
    BAND="bg"

    # Création du réseau hotspot
    sudo nmcli con add type wifi ifname "$WIFI_AP" con-name Slaybot ssid Slaybot mode ap
    sudo nmcli con modify Slaybot 802-11-wireless.band "$BAND"
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

    start_web_interface
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

# ---------------- WEB INTERFACE ----------------
start_web_interface() {
    echo "-------------------------------------------------------"
    echo "Démarrage de l'interface Web..."
    echo "Accédez à http://<votre_ip>:5000 pour configurer le hotspot."
    echo "-------------------------------------------------------"

    # Démarrer un serveur Flask pour l'interface Web
    python3 -m venv /home/hotspot/Documents/slaybot_hotspot/venv
    source /home/hotspot/Documents/slaybot_hotspot/venv/bin/activate
    pip install flask

    echo "[INFO] Flask installé."

    cat > /home/hotspot/Documents/slaybot_hotspot/app.py << EOF
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
EOF

    cat > /home/hotspot/Documents/slaybot_hotspot/templates/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Slaybot WiFi Router</title>
</head>
<body>
    <h1>Bienvenue sur l'interface Slaybot!</h1>
    <p>Configurez votre hotspot WiFi ici.</p>
</body>
</html>
EOF

    # Démarrer le serveur Flask
    cd /home/hotspot/Documents/slaybot_hotspot
    flask run --host=0.0.0.0 --port=5000 --debug
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