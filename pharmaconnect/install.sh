#!/bin/bash

# Script d'installation PharmaConnect Backend
echo "🚀 Installation PharmaConnect Backend..."

# Créer l'environnement virtuel si inexistant
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer les migrations
echo "🗄️ Création des migrations..."
python manage.py makemigrations

# Appliquer les migrations
echo "⚡ Application des migrations..."
python manage.py migrate

# Créer un superutilisateur (optionnel)
echo "👤 Création du superutilisateur..."
echo "from api.models import User; User.objects.create_superuser('admin', 'admin@pharmaconnect.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

echo "✅ Installation terminée !"
echo "🌐 Démarrer le serveur : python manage.py runserver"
echo "📚 Documentation API : http://127.0.0.1:8000/api/docs/"