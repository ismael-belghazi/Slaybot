import qrcode
import os

# Crée le dossier si inexistant
os.makedirs("qrcodes", exist_ok=True)

# Nombre de tables
num_tables = 10

# URL de base du site client
base_url = "https://monrestaurant.com/client?table="

for table in range(1, num_tables + 1):
    url = f"{base_url}{table}"
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    filename = f"qrcodes/table_{table}.png"
    img.save(filename)
    print(f"QR code pour Table {table} généré : {filename}")

print("Tous les QR codes ont été générés !")