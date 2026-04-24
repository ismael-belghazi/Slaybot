#!/bin/bash

set -e

echo "Mise à jour système..."
sudo apt update && sudo apt upgrade -y

echo "Installation dépendances essentielles..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-opencv \
    python3-picamera2 \
    rpicam-apps

echo "Création environnement virtuel..."
python3 -m venv venv

echo "Installation Python libs..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install numpy

echo "Test caméra..."
rpicam-hello || echo "Caméra non accessible"

echo "Terminé"

echo "Lancer avec :"
echo "./venv/bin/python ton_script.py"