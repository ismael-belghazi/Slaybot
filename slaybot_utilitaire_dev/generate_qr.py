import qrcode
import os
import uuid

# Crée le dossier si inexistant
os.makedirs("qrcodes", exist_ok=True)

# Table de test
table_test = 1

# Token universel temporaire pour tests
token_test = "TESTTOKEN123"

# URL locale avec token
base_url = f"http://127.0.0.1:5000/client?table={table_test}&token={token_test}"

# Génération du QR code
qr = qrcode.QRCode(version=1, box_size=10, border=4)
qr.add_data(base_url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
filename = f"qrcodes/table_{table_test}_test.png"
img.save(filename)

print(f"QR code de test généré : {filename}")
print(f"URL test : {base_url}")