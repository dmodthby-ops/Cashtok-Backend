#!/bin/bash
# Stop en cas d'erreur
set -e

echo "🚀 Démarrage du backend FastAPI..."

# Aller dans le dossier backend
cd backend

# Lancer Uvicorn (ASGI server) en mode production
# - Pas de reload (inutile en prod)
# - host 0.0.0.0 pour accepter les connexions externes
# - port 10000 car Render attend ça
# - 4 workers pour gérer plusieurs requêtes en parallèle
exec uvicorn index:app --host 0.0.0.0 --port 10000 --workers 4
