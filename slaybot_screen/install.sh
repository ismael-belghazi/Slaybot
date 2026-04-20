#!/bin/bash
set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$APP_DIR/venv"
FACE_FILE="$APP_DIR/face.py"

SERVICE_FACE="/etc/systemd/system/slaybot_face.service"
SERVICE_WIFI="/etc/systemd/system/slaybot_wifi.service"

WIFI_NAME="Slaybot"
WIFI_PASS="MHI-Hotspot"

echo "------------------------------------------------"
echo " SLAYBOT SYSTEM MANAGER"
echo "------------------------------------------------"
echo "1: Installer"
echo "2: Supprimer"
echo "3: Redemarrer affichage"
echo "------------------------------------------------"

read -p "Choix : " CHOICE

# ---------------- DETECT WIFI ----------------
WIFI_IFACE=$(iw dev | awk '$1=="Interface"{print $2}' | head -n 1)

if [ -z "$WIFI_IFACE" ]; then
    WIFI_IFACE="wlan0"
fi

# ---------------- INSTALL ----------------
install_all() {

    echo "[INSTALL] system update"
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-pip python3-tk python3-venv network-manager

    echo "[INSTALL] wifi config"

    sudo nmcli dev set "$WIFI_IFACE" managed yes

    for i in {1..10}; do
        nmcli dev wifi connect "$WIFI_NAME" password "$WIFI_PASS" ifname "$WIFI_IFACE" && break
        sleep 2
    done

    echo "[INSTALL] IP FIXE"
    sudo bash -c "cat > /etc/dhcpcd.conf <<EOF

interface $WIFI_IFACE
static ip_address=192.168.4.2/24
static routers=192.168.4.1
static domain_name_servers=8.8.8.8

EOF"

    echo "[INSTALL] python env"
    mkdir -p "$APP_DIR"
    python3 -m venv "$VENV_DIR"

    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel
    pip install websockets pyserial
    deactivate

    # ---------------- FACE FILE ----------------
    if [ ! -f "$FACE_FILE" ]; then
        cat > "$FACE_FILE" <<EOF
import tkinter as tk

root = tk.Tk()
root.title("SlayBot")
root.geometry("400x300")

label = tk.Label(root, text="SLAYBOT READY", font=("Arial", 18))
label.pack(expand=True)

root.mainloop()
EOF
    fi

    # ---------------- WIFI SERVICE ----------------
    sudo bash -c "cat > $SERVICE_WIFI <<EOF
[Unit]
Description=SlayBot WiFi Auto Connect
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c \"nmcli dev wifi connect $WIFI_NAME password $WIFI_PASS || true\"

[Install]
WantedBy=multi-user.target
EOF"

    # ---------------- FACE SERVICE ----------------
    sudo bash -c "cat > $SERVICE_FACE <<EOF
[Unit]
Description=SlayBot Face
After=network.target slaybot_wifi.service

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/python $FACE_FILE
Restart=always
RestartSec=2

User=$USER
Environment=DISPLAY=:0

[Install]
WantedBy=graphical.target
EOF"

    sudo systemctl daemon-reload
    sudo systemctl enable slaybot_wifi.service
    sudo systemctl enable slaybot_face.service
    sudo systemctl restart slaybot_face.service

    echo "INSTALL COMPLETE"
}

# ---------------- REMOVE ----------------
remove_all() {

    echo "[REMOVE] stop services"

    sudo systemctl stop slaybot_face.service || true
    sudo systemctl stop slaybot_wifi.service || true

    sudo systemctl disable slaybot_face.service || true
    sudo systemctl disable slaybot_wifi.service || true

    sudo rm -f "$SERVICE_FACE"
    sudo rm -f "$SERVICE_WIFI"

    sudo nmcli connection delete Slaybot || true

    sudo systemctl daemon-reload

    echo "REMOVED"
}

# ---------------- RESTART DISPLAY ----------------
restart_display() {

    echo "[RESTART] face service restart"

    sudo systemctl restart slaybot_face.service || true

    # fallback direct launch
    if ! systemctl is-active --quiet slaybot_face.service; then
        echo "[FALLBACK] manual start"
        cd "$APP_DIR"
        source "$VENV_DIR/bin/activate"
        python3 "$FACE_FILE" &
    fi

    echo "RESTART DONE"
}

# ---------------- MAIN ----------------
case "$CHOICE" in
    1) install_all ;;
    2) remove_all ;;
    3) restart_display ;;
    *) echo "Invalid choice" ;;
esac