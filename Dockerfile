# Utiliser une image de base Python qui n'est pas trop lourde
FROM python:3.9-slim

# Définit le répertoire de travail pour le conteneur
WORKDIR /app

# Copier les fichiers de dépendances 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Commande pour exécuter l'app
CMD ["python", "./src/main.py"]
