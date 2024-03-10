# Utiliser une image de base Python qui n'est pas trop lourde
FROM python:3.9-alpine

# Définit le répertoire de travail pour le conteneur
WORKDIR /app

# Installer les dépendances nécessaires
COPY requirements.txt .
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

# Copier le reste du code source de l'application dans le conteneur
COPY . .

# Commande pour exécuter l'app
CMD ["python", "./src/main.py"]
