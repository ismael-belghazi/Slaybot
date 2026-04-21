import subprocess
from concurrent.futures import ThreadPoolExecutor

base_ip = "10.42.0."

def ping(ip):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            print(f"{ip} est actif")
    except:
        pass

ips = [base_ip + str(i) for i in range(1, 255)]

with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(ping, ips)