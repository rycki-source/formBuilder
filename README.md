# FormBuilder - Application Complète

Application fullstack de création et gestion de formulaires dynamiques avec éditeur drag-and-drop.

## 🏗️ Architecture

### Backend
- **Framework** : FastAPI 0.115.0 (Python 3.11)
- **Base de données** : PostgreSQL 16
- **ORM** : SQLAlchemy 2.0.23 (async)
- **Cache** : Redis 7
- **Stockage** : MinIO (S3-compatible)
- **Déploiement** : Docker + Docker Compose

### Frontend
- **Framework** : React 18 + TypeScript
- **Build Tool** : Vite 7
- **Styling** : TailwindCSS 4
- **State Management** : Zustand 5
- **Routing** : React Router 7
- **Drag & Drop** : @dnd-kit

## 🚀 Démarrage rapide

```bash
# Backend (Docker)
cd formBuilder_backend
docker-compose up -d

# Frontend (npm)
cd ../frontend
npm install
npm run dev
```

- **Backend API** : http://localhost:8000
- **API Docs** : http://localhost:8000/docs
- **Frontend** : http://localhost:5173

## 📋 Fonctionnalités

### Gestion des utilisateurs
- Authentification JWT sécurisée
- Enregistrement et connexion
- Gestion de session
- Rôles et permissions

### Formulaires
- Création/édition de formulaires
- 9 types de champs disponibles
  - Texte, Email, Nombre, Date
  - Liste déroulante, Zone de texte
  - Case à cocher, Bouton radio, Fichier
- Éditeur drag-and-drop
- Configuration des propriétés de champs
- Publication/dépublication
- Validation des champs

### Soumissions
- Collecte des réponses
- Validation automatique
- Gestion des statuts (en attente, validée, rejetée)
- Export CSV/Excel/PDF

### Administration
- Dashboard avec statistiques
- Audit logging
- Gestion des référentiels
- Upload de fichiers
- Cache Redis pour performances

## 📁 Structure

```
formbuilder/
├── formBuilder_backend/
│   ├── app/
│   │   ├── api/          # Endpoints REST
│   │   ├── core/         # Configuration et sécurité
│   │   ├── db/           # Database et sessions
│   │   ├── models/       # Modèles SQLAlchemy
│   │   ├── schemas/      # Schémas Pydantic
│   │   ├── services/     # Logique métier
│   │   └── utils/        # Utilitaires
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── api/          # Clients API
    │   ├── components/   # Composants UI
    │   ├── features/     # FormBuilder
    │   ├── hooks/        # Hooks personnalisés
    │   ├── pages/        # Pages de l'app
    │   ├── store/        # Zustand stores
    │   └── types/        # Types TypeScript
    ├── package.json
    └── vite.config.ts
```

## 🔧 Technologies détaillées

### Backend Stack
```
FastAPI==0.115.0
SQLAlchemy==2.0.23
asyncpg==0.29.0
Alembic==1.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
redis==5.0.1
pandas==2.1.4
openpyxl==3.1.2
WeasyPrint==60.1
```

### Frontend Stack
```json
{
  "react": "^18.3.1",
  "react-router-dom": "^7.1.1",
  "zustand": "^5.0.2",
  "axios": "^1.7.9",
  "@dnd-kit/core": "^6.3.1",
  "tailwindcss": "^4.0.6",
  "lucide-react": "^0.468.0"
}
```

## 🔒 Sécurité

- JWT avec expiration configurable
- PEPPER additionnel pour hachage mot de passe
- CORS configuré
- Rate limiting
- Validation des entrées (Pydantic)
- Protection CSRF
- Sanitization des données

## 📊 API Endpoints

### Authentification
```
POST   /api/v1/auth/login
POST   /api/v1/auth/register
GET    /api/v1/auth/me
POST   /api/v1/auth/logout
```

### Formulaires
```
GET    /api/v1/formulaires
GET    /api/v1/formulaires/{id}
POST   /api/v1/formulaires
PUT    /api/v1/formulaires/{id}
DELETE /api/v1/formulaires/{id}
POST   /api/v1/formulaires/{id}/publier
POST   /api/v1/formulaires/{id}/depublier
```

### Soumissions
```
GET    /api/v1/soumissions
GET    /api/v1/soumissions/{id}
POST   /api/v1/soumissions
PUT    /api/v1/soumissions/{id}/statut
DELETE /api/v1/soumissions/{id}
```

### Exports
```
POST   /api/v1/exports/csv
POST   /api/v1/exports/excel
POST   /api/v1/exports/pdf
```

### Référentiels
```
GET    /api/v1/referentiels
POST   /api/v1/referentiels
POST   /api/v1/referentiels/import-excel
```

## 🎨 Interface utilisateur

### Pages
- **Login** : Authentification sécurisée
- **Dashboard** : Vue d'ensemble et statistiques
- **Liste des formulaires** : Gestion complète avec filtres
- **Form Builder** : Éditeur drag-and-drop avec palette de champs

### Composants réutilisables
- Button (4 variantes)
- Input (avec validation)
- Card (conteneur stylisé)
- Layout (navigation)
- ProtectedRoute (authentification)

## 📈 Performance

- **Cache Redis** pour requêtes fréquentes
- **Connexions async** pour PostgreSQL
- **Lazy loading** des composants React
- **Code splitting** avec Vite
- **Optimisation des images**
- **Compression gzip**

## 🧪 Tests

### Backend
```bash
cd formBuilder_backend
pytest tests/
```

### Frontend
```bash
cd frontend
npm run test  # À configurer
```

## 📝 Documentation

- [Guide de démarrage](QUICKSTART.md)
- [Backend README](formBuilder_backend/ReadMe.md)
- [Frontend README](frontend/README.md)
- [API Documentation](http://localhost:8000/docs)

## 🚧 Développement

### Backend
```bash
# Lancer en mode dev (sans Docker)
cd formBuilder_backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
# Hot reload activé par défaut
cd frontend
npm run dev
```

## 🐛 Débogage

### Logs Backend
```bash
docker-compose logs -f backend
```

### Logs Frontend
- Console navigateur (F12)
- React DevTools
- Network tab pour API calls

## 🔄 Workflow Git

```bash
# Créer une branche
git checkout -b feature/nouvelle-fonctionnalite

# Commit
git add .
git commit -m "feat: description"

# Push
git push origin feature/nouvelle-fonctionnalite
```

## 📦 Déploiement production

### Backend
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Frontend
```bash
npm run build
# Servir le dossier dist/
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Projet FormBuilder - 2024

## 👥 Auteurs

Développé avec ❤️ par l'équipe FormBuilder

---

**Pour plus d'informations, consultez la documentation dans chaque sous-dossier.**
