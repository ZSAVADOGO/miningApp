########################
# 1. BUILD STAGE
########################
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances système nécessaires à la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

# Ressources NLTK
RUN python - <<EOF
import nltk
nltk.download("punkt")
nltk.download("stopwords")
EOF


########################
# 2. RUNTIME STAGE
########################
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances runtime seulement (plus léger)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi8 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copier les libs Python compilées
COPY --from=builder /install /usr/local

# Copier les données NLTK
COPY --from=builder /root/nltk_data /root/nltk_data

# Copier le projet
COPY . .

# Collecte des fichiers statiques
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Serveur WSGI PRO
CMD ["gunicorn", "miningApp.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
