# FormBuilder API

API FastAPI pour la génération dynamique de formulaires métier.

## Démarrage rapide

### Installation

\`\`\`bash
# 1. Cloner le repository
git clone https://github.com/rycki-source/formbuilder.git
cd formbuilder/backend

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
\`\`\`

### Démarrage avec Docker

\`\`\`bash
cd ..
docker-compose up -d
\`\`\`

### Démarrage local

\`\`\`bash
uvicorn app.main:app --reload --port 8000
\`\`\`

##  Documentation

- API Docs: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Health Check: <http://localhost:8000/health>

## Architecture

- **FastAPI** - Framework web asynchrone
- **SQLAlchemy 2.0** - ORM async
- **PostgreSQL 16** - Base de données
- **Redis** - Cache
- **MinIO** - Stockage fichiers (S3-compatible)

## Tests

\`\`\`bash
pytest
pytest --cov=app tests/
\`\`\`

## 📋 Endpoints

### Authentication

- `POST /api/v1/auth/register` - Créer un compte
- `POST /api/v1/auth/login` - Se connecter
- `GET /api/v1/auth/me` - Profil utilisateur

### Formulaires

- `POST /api/v1/formulaires/` - Créer un formulaire
- `GET /api/v1/formulaires/` - Lister les formulaires
- `GET /api/v1/formulaires/{id}` - Récupérer un formulaire
- `PUT /api/v1/formulaires/{id}` - Mettre à jour
- `DELETE /api/v1/formulaires/{id}` - Supprimer

### Soumissions

- `POST /api/v1/soumissions/` - Soumettre un formulaire
- `GET /api/v1/soumissions/` - Lister les soumissions
- `GET /api/v1/soumissions/{id}` - Récupérer une soumission

## 📝 License

MIT
