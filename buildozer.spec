# =============================================================================
#  CONFIG BUILDOZER - LE GUIDE DU SURVIE POUR RSapp
# =============================================================================
# Ce fichier, c'est la magie pour transformer ton code Python 
# en une application Android qui tourne pour de vrai.

[app]
# Le nom qui va s'afficher fièrement sous l'icône sur ton écran d'accueil
title = Robot-Server

# Le nom technique. Pas d'espaces ici, c'est ce que le système Android utilise.
package.name = RSapp

# Ton "ID" de développeur. On met souvent l'inverse d'un nom de domaine.
package.domain = com.mhi_robotics

# Où est ton code ? "." veut dire "tout ce qui est dans ce dossier"
source.dir = .

# Les fichiers qu'on embarque dans le téléphone. 
# N'oublie pas le .json pour stocker la config 
source.include_exts = py,png,jpg,kv,atlas,json

# On ignore les trucs inutiles (tests, environnements virtuels) pour pas que 
# l'application soit léger
source.exclude_dirs = tests, bin, venv, .buildozer

# version de l'application
version = 0.5

# Tout ce que ton code "import" doit être ici.
# On rajoute openssl et urllib3 parce qu'Android est un peu capricieux avec le réseau.
requirements = python3, kivy, requests, websocket-client, openssl, urllib3, charset-normalizer, idna

# On force le mode Paysage 
orientation = landscape

# 0 = On garde la barre d'heure et de batterie en haut. Plus propre pour debugger.
fullscreen = 0

# --- Partie ANDROID ---

# On demande l'accès au Wi-Fi. Sinon, rien ne passera.
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# On vise Android 13 (le standard actuel). C'est ce que Google réclame.
android.api = 33

# On accepte les vieux téléphones jusqu'à Android 7.0 (API 24). 
android.minapi = 24

# La version de la "boîte à outils" (NDK). La 25b est la plus stable pour Kivy.
android.ndk = 25b
android.ndk_api = 24

# On compile pour les téléphones récents (64-bit) et les plus anciens (32-bit).
android.archs = arm64-v8a, armeabi-v7a

# On laisse Java faire son boulot en arrière-plan.
android.use_javac = True

# "Proguard" : ça nettoie et compresse le code pour que l'APK soit plus léger.
android.proguard = True

# Pour débugger : ça permet de voir tes "print" dans la console avec 'adb logcat'
android.logcat_filters = *:S python:D

# --- OPTIONS BUILDOZER ---

[buildozer]
# 1 = Normal. Si ça plante, passe-le à 2 pour avoir TOUS les détails (ca envoie enromement d'information !)
log_level = 1

# On évite de lancer ça en "root", c'est souvent source de problemes.
warn_on_root = 1