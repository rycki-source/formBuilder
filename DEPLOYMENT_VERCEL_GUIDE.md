# 🚀 Guide de Déploiement sur Vercel

Guide complet pour déployer l'application FormBuilder sur Vercel.

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Architecture de Déploiement](#architecture-de-déploiement)
3. [Configuration de la Base de Données](#configuration-de-la-base-de-données)
4. [Déploiement du Frontend](#déploiement-du-frontend)
5. [Déploiement du Backend](#déploiement-du-backend)
6. [Configuration des Variables d'Environnement](#configuration-des-variables-denvironnement)
7. [Post-Déploiement](#post-déploiement)
8. [Dépannage](#dépannage)

---

## Prérequis

### Comptes Nécessaires

- ✅ Compte [Vercel](https://vercel.com) (gratuit)
- ✅ Compte [GitHub](https://github.com) (pour CI/CD)
- ✅ Base de données PostgreSQL hébergée :
  - [Vercel Postgres](https://vercel.com/storage/postgres) (recommandé)
  - [Supabase](https://supabase.com) (gratuit)
  - [Neon](https://neon.tech) (gratuit)
  - [Railway](https://railway.app)

### Outils Locaux

```bash
# Installer Vercel CLI
npm install -g vercel

# Vérifier l'installation
vercel --version
```

---

## Architecture de Déploiement

```
┌─────────────────────────────────────────┐
│           Vercel Platform               │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────┐  ┌───────────────┐  │
│  │   Frontend    │  │   Backend     │  │
│  │  (React/Vite) │  │   (FastAPI)   │  │
│  │  Port: 443    │  │  Serverless   │  │
│  └───────┬───────┘  └───────┬───────┘  │
│          │                  │          │
│          └──────────┬───────┘          │
└─────────────────────┼──────────────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │  PostgreSQL Database  │
          │   (Vercel Postgres/   │
          │    Supabase/Neon)     │
          └───────────────────────┘
```

---

## Configuration de la Base de Données

### Option 1 : Vercel Postgres (Recommandé)

1. **Créer une base de données Vercel Postgres**

```bash
# Depuis votre projet Vercel
vercel storage create postgres
```

2. **Ou via le Dashboard**
   - Allez sur https://vercel.com/dashboard
   - Sélectionnez votre projet
   - Storage → Create Database → Postgres

3. **Récupérer les credentials**
   - Copiez `POSTGRES_URL` depuis le dashboard
   - Format : `postgresql://user:password@host:port/database`

### Option 2 : Supabase (Gratuit)

1. Créer un projet sur https://supabase.com
2. Aller dans Settings → Database
3. Copier la "Connection string" (mode Direct)
4. Format : `postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres`

### Option 3 : Neon (Gratuit)

1. Créer un projet sur https://neon.tech
2. Copier la connection string
3. Format : `postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb`

### Initialiser la Base de Données

```bash
# 1. Installer psql ou utiliser un client PostgreSQL
# 2. Se connecter à la base de données
psql "votre_connection_string"

# 3. Exécuter le schéma (dans le terminal psql)
\i formBuilder_backend/database_schema_20251212_100605.sql

# Ou avec un fichier local
psql "votre_connection_string" < formBuilder_backend/database_schema_20251212_100605.sql
```

---

## Déploiement du Frontend

### 1. Préparer le Frontend

Créez `frontend/.env.production` :

```env
VITE_API_URL=https://votre-backend.vercel.app/api/v1
```

### 2. Configuration Vercel

Créez `frontend/vercel.json` :

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### 3. Déployer via CLI

```bash
# Se placer dans le dossier frontend
cd frontend

# Login Vercel
vercel login

# Déployer
vercel --prod

# Suivre les instructions :
# - Link to existing project? No
# - Project name: formbuilder-frontend
# - Directory: ./
# - Override settings? No
```

### 4. Déployer via GitHub (Recommandé)

1. **Pousser le code sur GitHub**

```bash
# À la racine du projet
git add .
git commit -m "Ready for Vercel deployment"
git push origin master
```

2. **Configurer sur Vercel**
   - Aller sur https://vercel.com/new
   - Import Git Repository → Sélectionner votre repo
   - Framework Preset : Vite
   - Root Directory : `frontend`
   - Build Command : `npm run build`
   - Output Directory : `dist`
   - Install Command : `npm install`

3. **Variables d'environnement**
   - Ajouter `VITE_API_URL` dans Settings → Environment Variables

---

## Déploiement du Backend

### 1. Adapter le Backend pour Vercel

Créez `formBuilder_backend/vercel.json` :

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.11"
  }
}
```

### 2. Créer un fichier `requirements.txt` optimisé

```bash
cd formBuilder_backend

# Générer requirements.txt
pip freeze > requirements.txt
```

Vérifiez que `requirements.txt` contient au minimum :

```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
alembic>=1.13.0
openpyxl>=3.1.0
pandas>=2.0.0
```

### 3. Modifier `app/main.py` pour Vercel

Ajoutez au début du fichier :

```python
import os
from mangum import Mangum

# ... votre code existant ...

# Pour Vercel serverless
handler = Mangum(app)
```

Installez mangum :

```bash
pip install mangum
echo "mangum" >> requirements.txt
```

### 4. Configuration CORS

Dans `formBuilder_backend/app/main.py`, mettez à jour CORS :

```python
# Configuration CORS pour production
origins = [
    "https://votre-frontend.vercel.app",  # Votre frontend
    "http://localhost:5173",              # Dev local
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. Déployer le Backend

**Via CLI :**

```bash
cd formBuilder_backend
vercel --prod
```

**Via GitHub :**

1. Créer un nouveau projet Vercel
2. Root Directory : `formBuilder_backend`
3. Framework Preset : Other
4. Build Command : `pip install -r requirements.txt`
5. Output Directory : `.`

---

## Configuration des Variables d'Environnement

### Variables Frontend (Vercel Dashboard)

```env
VITE_API_URL=https://votre-backend.vercel.app/api/v1
```

### Variables Backend (Vercel Dashboard)

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Security
SECRET_KEY=votre_secret_key_super_securisee_32_caracteres_minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
FRONTEND_URL=https://votre-frontend.vercel.app

# Optional
ENVIRONMENT=production
DEBUG=false
```

### Générer une SECRET_KEY sécurisée

```python
# Exécuter dans Python
import secrets
print(secrets.token_urlsafe(32))
```

Ou avec OpenSSL :

```bash
openssl rand -base64 32
```

---

## Post-Déploiement

### 1. Vérifier les Déploiements

```bash
# Frontend
curl https://votre-frontend.vercel.app

# Backend (health check)
curl https://votre-backend.vercel.app/api/v1/health

# API Docs
# Ouvrir dans le navigateur
https://votre-backend.vercel.app/docs
```

### 2. Tester l'Application

1. **Créer un compte utilisateur**
   - Aller sur votre frontend
   - S'inscrire avec un email valide

2. **Tester les fonctionnalités**
   - Connexion
   - Création de formulaire
   - Import Excel
   - Soumission

### 3. Configuration des Domaines (Optionnel)

**Frontend :**
- Vercel Dashboard → Settings → Domains
- Ajouter : `votredomaine.com`
- Configurer DNS selon les instructions

**Backend :**
- Ajouter : `api.votredomaine.com`
- Mettre à jour `VITE_API_URL` dans le frontend

### 4. Monitoring

Activez les Analytics Vercel :
- Dashboard → Analytics
- Surveillez les erreurs et performances

---

## Dépannage

### Erreur : "Database connection failed"

**Solution :**
```bash
# Vérifier la connection string
vercel env pull

# Tester localement
python
>>> from sqlalchemy import create_engine
>>> engine = create_engine("votre_database_url")
>>> engine.connect()
```

### Erreur : "Module not found"

**Solution :**
```bash
# Vérifier requirements.txt
pip freeze > requirements.txt

# Redéployer
vercel --prod --force
```

### Erreur CORS

**Solution :**

Dans `formBuilder_backend/app/main.py` :

```python
origins = [
    "https://*.vercel.app",  # Autoriser tous les sous-domaines Vercel
    "https://votre-domaine.com",
]
```

### Frontend ne trouve pas le backend

**Solution :**

Vérifiez `.env.production` :

```env
# DOIT commencer par VITE_
VITE_API_URL=https://votre-backend.vercel.app/api/v1
```

Rebuild le frontend :

```bash
vercel --prod --force
```

### Erreur 500 sur le Backend

**Solution :**

Voir les logs :

```bash
vercel logs votre-backend-url --follow
```

Vérifier :
- Variables d'environnement correctes
- Database accessible
- Migrations exécutées

### Timeout sur les requêtes longues

**Solution :**

Vercel Serverless a une limite de 10s (gratuit) / 60s (Pro).

Pour les imports Excel longs, considérez :
- Augmenter à Vercel Pro
- Ou utiliser [Railway](https://railway.app) pour le backend (toujours actif)

---

## Alternative : Backend sur Railway

Si vous rencontrez des limites avec Vercel Serverless :

### 1. Créer un compte Railway

https://railway.app

### 2. Déployer le Backend

```bash
# Installer Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialiser
cd formBuilder_backend
railway init

# Déployer
railway up

# Ajouter PostgreSQL
railway add postgresql

# Variables d'environnement auto-configurées
```

### 3. Mettre à jour le Frontend

```env
VITE_API_URL=https://votre-app.railway.app/api/v1
```

---

## Checklist de Déploiement

- [ ] Base de données PostgreSQL créée et accessible
- [ ] Schéma de base de données importé
- [ ] Variables d'environnement configurées (frontend + backend)
- [ ] CORS configuré correctement
- [ ] Frontend déployé sur Vercel
- [ ] Backend déployé sur Vercel (ou Railway)
- [ ] URL du backend configurée dans le frontend
- [ ] Tests de connexion réussis
- [ ] Création de compte utilisateur fonctionne
- [ ] Login fonctionne
- [ ] Création de formulaire fonctionne
- [ ] Import Excel fonctionne
- [ ] Domaines personnalisés configurés (optionnel)

---

## Ressources Utiles

- 📚 [Documentation Vercel](https://vercel.com/docs)
- 🐍 [Vercel Python](https://vercel.com/docs/functions/runtimes/python)
- ⚡ [Vite Deployment](https://vitejs.dev/guide/static-deploy.html#vercel)
- 🔒 [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
- 🗄️ [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres)

---

## Support

Pour toute question ou problème :

1. Consultez les logs Vercel : `vercel logs`
2. Vérifiez la [documentation Vercel](https://vercel.com/docs)
3. Ouvrez une issue sur GitHub

**Bon déploiement ! 🚀**
