import os
import subprocess
import psutil
import spidev
from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder='.')

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_mcp3008(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def get_battery_cells():
    cells = []
    # Lecture des 4 cellules sur CH0, CH1, CH2, CH3
    for i in range(4):
        raw = read_mcp3008(i)
        voltage = round((raw * 3.3 / 1023.0) * 5.15, 2) 
        cells.append(voltage)
    return cells

def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = float(f.read()) / 1000.0
            return round(temp, 1)
    except Exception:
        return "N/A"

def get_network_status(interface):
    try:
        cmd = f"nmcli -t -f DEVICE,STATE,CONNECTION device | grep ^{interface}"
        output = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        parts = output.split(':')
        if len(parts) >= 3 and parts[1] == "connected":
            return "ONLINE", parts[2]
        return "OFFLINE", "NONE"
    except:
        return "ERROR", "N/A"

def get_signal_strength(interface):
    try:
        cmd = f"nmcli -f IN-USE,SIGNAL,DEVICE dev wifi | grep '*' | grep {interface} | awk '{{print $2}}'"
        signal = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return signal if signal else "0"
    except:
        try:
            cmd = f"grep {interface} /proc/net/wireless | awk '{{print int($3 * 100 / 70)}}'"
            return subprocess.output(cmd, shell=True).decode("utf-8").strip()
        except:
            return "0"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/stats")
def stats():
    # RAM via commande système
    try:
        cmd = "free | grep Mem | awk '{print $3/$2 * 100.0}'"
        ram_val = float(subprocess.check_output(cmd, shell=True).decode())
    except:
        ram_val = 0

    # CPU via top
    try:
        cmd = "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\\1/' | awk '{print 100 - $1}'"
        cpu_val = float(subprocess.check_output(cmd, shell=True).decode())
    except:
        cpu_val = 0

    # Réseau
    w1_status, w1_ssid = get_network_status("wlan1")
    w1_signal = get_signal_strength("wlan1")
    w0_status, _ = get_network_status("wlan0")
    
    # Batterie
    battery_cells = get_battery_cells()

    return jsonify(
        cpu_usage=round(cpu_val, 1),
        ram_usage=round(ram_val, 1),
        inet_signal=w1_signal,
        cpu_temp=get_cpu_temperature(),
        inet_ssid=w1_ssid,
        ap_status=w0_status,
        cells=battery_cells
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)