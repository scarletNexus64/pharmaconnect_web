# PharmaConnect Backend API

## 🎯 Description

API REST complète pour la gestion des produits médicaux pour ONG et programmes étatiques, développée avec Django REST Framework.

## 🚀 Installation rapide

### Méthode 1: Script automatique
```bash
chmod +x install.sh
./install.sh
```

### Méthode 2: Installation manuelle

1. **Créer l'environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

2. **Installer les dépendances**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Configuration**
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

4. **Base de données**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optionnel
```

5. **Démarrer le serveur**
```bash
python manage.py runserver
```

## 📚 Documentation

- **API Documentation**: http://127.0.0.1:8000/api/docs/
- **Admin Interface (Jazzmin)**: http://127.0.0.1:8000/admin/
- **API Base URL**: http://127.0.0.1:8000/api/
- **Configuration Jazzmin**: [JAZZMIN_CONFIG.md](./JAZZMIN_CONFIG.md)

## 🔧 Endpoints principaux

### Authentification
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/logout/` - Déconnexion

### Configuration
- `GET|POST /api/organizations/` - Organisations/ONG
- `GET|POST /api/donors/` - Bailleurs de fonds
- `GET|POST /api/health-facilities/` - Formations sanitaires
- `GET|POST /api/projects/` - Projets

### Médicaments
- `GET|POST /api/medications/` - Référentiel médicaments
- `GET /api/medications/search/?q=terme` - Recherche
- `GET|POST /api/standard-lists/` - Listes standard
- `POST /api/standard-lists/generate_standard_list/` - Génération auto

### Stocks et Dispensation
- `GET|POST /api/stock-entries/` - Entrées en stock
- `GET|POST /api/dispensations/` - Dispensations
- `GET|POST /api/inventories/` - Inventaires
- `GET|POST /api/consumption-data/` - Données consommation

### Analytics
- `GET /api/analytics/stock-summary/` - Résumé stocks
- `GET /api/analytics/pharmacoepidemio/` - Analytics épidémiologiques
- `GET|POST /api/alerts/` - Système d'alertes

## 🔐 Authentification

Utiliser le token obtenu lors de la connexion :
```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" http://127.0.0.1:8000/api/medications/
```

## 🗄️ Base de données

### Développement (SQLite)
Par défaut, utilise SQLite (fichier `db.sqlite3`)

### Production (PostgreSQL)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/pharmaconnect
```

## 🧪 Tests

```bash
# Installer dépendances test
pip install -r requirements-dev.txt

# Lancer les tests
python manage.py test

# Avec pytest
pytest

# Coverage
coverage run --source='.' manage.py test
coverage report
```

## 📁 Structure du projet

```
pharmaconnect/
├── api/                    # Application principale
│   ├── models.py          # Modèles de données
│   ├── views.py           # Vues API
│   ├── serializers.py     # Sérialiseurs DRF
│   ├── urls.py            # URLs API
│   └── admin.py           # Administration Django
├── pharmaconnect/         # Configuration Django
│   ├── settings.py        # Paramètres
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # WSGI
├── media/                 # Fichiers uploadés
├── requirements.txt       # Dépendances production
├── requirements-dev.txt   # Dépendances développement
└── manage.py             # CLI Django
```

## 🔄 Migration et données

### Import données Excel existantes
```python
# Exemple d'import via shell Django
python manage.py shell
>>> from api.models import Medication, MedicationCategory
>>> # Votre logique d'import ici
```

### Fixtures (données de test)
```bash
python manage.py loaddata fixtures/sample_data.json
```

## 🚀 Déploiement

### Docker (recommandé)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "pharmaconnect.wsgi:application"]
```

### Variables d'environnement production
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🎨 Interface d'administration

### Django Jazzmin intégré
- **Interface moderne** avec thème responsive
- **Dashboard personnalisé** avec statistiques temps réel
- **Icônes thématiques** pour chaque module médical
- **Navigation optimisée** pour la gestion pharmaceutique

### Connexion admin
```
URL: http://127.0.0.1:8000/admin/
Utilisateur: admin
Mot de passe: admin123
```

### Fonctionnalités admin
- 📊 **Dashboard analytique** avec graphiques
- 🔍 **Recherche globale** dans médicaments et organisations  
- 📱 **Interface responsive** pour tablettes
- 🎨 **Mode sombre** disponible
- 🚀 **Liens rapides** vers API et documentation

## 📞 Support

Pour les questions techniques ou contributions :
- Issues GitHub
- Documentation API interactive : `/api/docs/`
- Admin Django : `/admin/`

## 📄 Licence

Projet développé pour la gestion pharmaceutique dans les ONG et programmes de santé publique.