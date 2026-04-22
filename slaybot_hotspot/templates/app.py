import os
import subprocess
import psutil
from flask import Flask, render_template, jsonify

# On configure Flask pour qu'il cherche l'index.html dans le dossier actuel
# puisque ton app.py est lui-même dans le dossier /templates
app = Flask(__name__, template_folder='.')

def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = float(f.read()) / 1000.0
            return round(temp, 1)
    except Exception:
        return "N/A"

def get_ram_usage():
    try:
        return psutil.virtual_memory().percent
    except Exception:
        return 0

def get_network_status(interface):
    try:
        # Utilisation de nmcli pour voir si l'interface est active
        output = subprocess.check_output("nmcli -t -f NAME,TYPE,DEVICE connection show --active", shell=True)
        output = output.decode("utf-8").strip().splitlines()
        for line in output:
            parts = line.split(":")
            if len(parts) < 3: continue
            name, ctype, device = parts[0], parts[1], parts[2]
            if device == interface:
                return "Connecté", name
        return "Non connecté", "Aucun"
    except Exception:
        return "Erreur", "N/A"

def get_signal_strength(interface, target_ssid=None):
    try:
        output = subprocess.check_output(f"nmcli -f SSID,SIGNAL dev wifi list ifname {interface}", shell=True)
        lines = output.decode("utf-8").strip().splitlines()
        for line in lines[1:]:
            parts = line.split()
            if not parts: continue
            signal = parts[-1]
            ssid = " ".join(parts[:-1])
            if target_ssid and target_ssid in ssid:
                return signal
        return "0"
    except Exception:
        return "0"

@app.route("/")
def home():
    # Affiche la page index.html située dans le même dossier
    return render_template("index.html")

@app.route("/stats")
def stats():
    # Récupération des infos réseau
    wlan1_status, wlan1_ssid = get_network_status("wlan1")
    wlan1_signal = get_signal_strength("wlan1", wlan1_ssid) if wlan1_status == "Connecté" else "0"
    
    # Récupération de l'état du Hotspot (wlan0)
    wlan0_status, _ = get_network_status("wlan0")
    
    return jsonify(
        cpu_temp=get_cpu_temperature(),
        cpu_usage=psutil.cpu_percent(),
        ram_usage=get_ram_usage(),
        inet_ssid=wlan1_ssid,
        inet_signal=wlan1_signal,
        ap_status=wlan0_status
    )

if __name__ == "__main__":
    # host='0.0.0.0' permet l'accès depuis le 10.42.0.1 ET l'IP du réseau raspberry
    app.run(host='0.0.0.0', port=5000, debug=False)