FROM ubuntu:22.04

# --- CONFIGURATION DE L'ENVIRONNEMENT ---
ENV DEBIAN_FRONTEND=noninteractive
ENV USER=buildozer
ENV HOME=/home/buildozer
# On injecte les binaires Python locaux dans le PATH pour que 'buildozer' soit reconnu
ENV PATH="$HOME/.local/bin:$PATH"
ENV PYTHONPATH=$HOME/.local/lib/python3.10/site-packages

# --- INSTALLATION DES DÉPENDANCES SYSTÈME ---
# Ces paquets sont indispensables pour compiler les recettes Python vers Android (C, C++, Java)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-dev python3-pip git zip unzip openjdk-17-jdk \
    ccache build-essential autoconf libtool pkg-config libffi-dev \
    # Libssl et Zlib sont critiques pour les requêtes réseau (requests/openssl)
    libssl-dev zlib1g-dev curl sudo cmake mesa-common-dev libgles2-mesa-dev \
    && rm -rf /var/lib/apt/lists/*

# --- GESTION DES PERMISSIONS ---
# Création d'un utilisateur dédié. Buildozer refuse souvent de tourner en 'root'.
RUN useradd -m -s /bin/bash $USER \
 && echo "$USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER buildozer
WORKDIR $HOME/app

# --- INSTALLATION DES OUTILS DE BUILD ---
# On fixe les versions de Cython et Pyjnius pour éviter les incompatibilités avec Kivy
RUN python3 -m pip install --upgrade pip \
 && pip install --user --no-cache-dir buildozer cython==0.29.36 pyjnius==1.4.2

# Création des dossiers de cache pour permettre le montage de volumes externes
RUN mkdir -p $HOME/.buildozer $HOME/.gradle
COPY --chown=buildozer:buildozer buildozer.spec $HOME/app/

# --- PRÉ-BACKING ---
# Cette ligne "fantôme" force Buildozer à initialiser ses outils sans lancer de build réel
RUN buildozer android p4a -- help || true

# Copie finale du code source
COPY --chown=buildozer:buildozer . $HOME/app

# Lancement automatique de la compilation au démarrage du conteneur
CMD ["buildozer", "android", "debug"]