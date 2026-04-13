# Utilise l'image Python officielle
FROM python:3.11-slim

# Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Crée le répertoire de l'app
WORKDIR /app

# Copie requirements et installe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste de l'application
COPY . .

# Expose le port Flask
EXPOSE 5000

# Commande pour lancer l'application
CMD ["python", "app.py"]