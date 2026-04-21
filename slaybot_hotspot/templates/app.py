from flask import Flask, render_template
import psutil
import subprocess

app = Flask(__name__)

def get_network_status():
    try:
        output = subprocess.check_output("nmcli -t -f ACTIVE,SSID dev wifi", shell=True)
        output = output.decode("utf-8").strip().splitlines()
        for line in output:
            if line.startswith("yes"):
                ssid = line.split(":")[1]
                return "Connecté", ssid
        return "Non connecté", "Aucun"
    except Exception as e:
        print(f"Erreur dans get_network_status: {str(e)}")  # Log
        return "Erreur", f"Erreur réseau : {str(e)}"

def get_signal_strength():
    try:
        output = subprocess.check_output("nmcli device wifi list ifname wlan1", shell=True)
        output = output.decode("utf-8").strip().splitlines()
        for line in output:
            if "raspberry" in line:
                parts = line.split()
                signal = parts[-2]
                return int(signal)
        return 0
    except Exception as e:
        print(f"Erreur dans get_signal_strength: {str(e)}")  # Log
        return 0

def get_cpu_temperature():
    try:
        temp = psutil.sensors_temperatures().get('cpu_thermal', [])
        if temp:
            return temp[0].current
        else:
            output = subprocess.check_output("vcgencmd measure_temp", shell=True)
            temp = output.decode("utf-8").strip().split('=')[1].replace("C", "")
            return temp
    except Exception as e:
        print(f"Erreur dans get_cpu_temperature: {str(e)}")  # Log
        return "Inconnu"

def get_cpu_usage():
    try:
        return psutil.cpu_percent(interval=1)
    except Exception as e:
        print(f"Erreur dans get_cpu_usage: {str(e)}")  # Log
        return 0

def get_ram_usage():
    try:
        memory = psutil.virtual_memory()
        return round(memory.used / (1024 ** 3), 2)
    except Exception as e:
        print(f"Erreur dans get_ram_usage: {str(e)}")  # Log
        return 0

def get_available_networks():
    try:
        output = subprocess.check_output("nmcli -t -f SSID dev wlan0 wifi", shell=True)
        output = output.decode("utf-8").strip().splitlines()
        networks = [line for line in output if line != "Slaybot"]
        return networks
    except Exception as e:
        print(f"Erreur dans get_available_networks: {str(e)}")  
        return []  # Retourne une liste vide en cas d'erreur

@app.route("/")
def home():
    # Récupérer les informations système et réseau
    try:
        network_status, current_ssid = get_network_status()
        signal_strength = get_signal_strength()
        cpu_temperature = get_cpu_temperature()
        cpu_usage = get_cpu_usage()
        ram_usage = get_ram_usage()
        available_networks = get_available_networks()

        # Log pour vérifier les valeurs récupérées
        print(f"Network Status: {network_status}")
        print(f"Current SSID: {current_ssid}")
        print(f"Signal Strength: {signal_strength}")
        print(f"CPU Temperature: {cpu_temperature}")
        print(f"CPU Usage: {cpu_usage}")
        print(f"RAM Usage: {ram_usage}")
        print(f"Available Networks: {available_networks}")

        # Log les données envoyées au template
        print(f"Rendering template with the following data: {network_status}, {current_ssid}, {signal_strength}, {cpu_temperature}, {cpu_usage}, {ram_usage}, {available_networks}")

        return render_template("index.html", 
                               network_status=network_status,
                               current_ssid=current_ssid,
                               signal_strength=signal_strength,
                               cpu_temperature=cpu_temperature,
                               cpu_usage=cpu_usage,
                               ram_usage=ram_usage,
                               available_networks=available_networks)
    except Exception as e:
        print(f"Erreur dans la fonction home: {str(e)}")  # Log
        return "Erreur dans le traitement des données. Vérifiez les logs pour plus d'informations."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)