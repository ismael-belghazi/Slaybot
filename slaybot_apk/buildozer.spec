# =============================================================================
#  CONFIG BUILDOZER - VERSION OPTIMISÉE POUR RSapp
# =============================================================================

[app]
# Nom affiché sous l'icône
title = Robot-Server

# Nom technique utilisé par Android
package.name = RSapp
package.domain = com.mhi_robotics

# Code source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.exclude_dirs = tests, bin, venv, .buildozer

# Version de l'application
version = 0.7

# Bibliothèques Python à inclure
# On fixe les versions pour éviter les conflits avec p4a
requirements = python3,kivy==2.3.1,kivymd==1.1.1,pyserial,websocket-client,requests,pyjnius==1.4.2,filetype

# Orientation et affichage
orientation = landscape
fullscreen = 0

# --- Partie ANDROID ---
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 24

# NDK / architectures
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a

# Compilation Java et optimisation APK
android.use_javac = True
android.proguard = True

# Debugging avec logcat
android.logcat_filters = *:S python:D

[buildozer]
# Niveau de log élevé pour voir tous les détails d'erreur
log_level = 2

# Avertir si lancé en root
warn_on_root = 1

# Répertoire de stockage sans espace
storage_dir = ./.buildozer_storage

# Désactiver l'utilisation de git dans le build
use_git = 0