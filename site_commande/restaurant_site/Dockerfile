# Utilise Python officiel slim
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Crée le répertoire de l'application
WORKDIR /app

# Installe les dépendances système nécessaires à eventlet
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie les fichiers de dépendances
COPY requirements.txt .

# Installe pip et les dépendances Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copie le code de l'application
COPY . .

# Expose le port Flask
EXPOSE 5000

# Commande pour exécuter l'application avec Eventlet
CMD ["python", "app.py"]