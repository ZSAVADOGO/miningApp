FROM python:3.11-slim

# Variables propres
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dossier de travail
WORKDIR /app

# Dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Télécharger les ressources NLTK nécessaires
RUN python -m nltk.downloader punkt stopwords
RUN python -m nltk.downloader punkt punkt_tab stopwords

# Code du projet
COPY . .

# Port Django
EXPOSE 8000

# Lancer le serveur
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
