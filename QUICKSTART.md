# Guide de Démarrage - FormBuilder

## 📋 Prérequis

- Docker Desktop installé et en cours d'exécution
- Node.js (v18+) et npm installés
- Git (optionnel)

## 🚀 Démarrage rapide

### 1. Backend (FastAPI + Docker)

```bash
# Naviguer vers le répertoire backend
cd c:\Users\DELL\formbuilder\formBuilder_backend

# Démarrer tous les services avec Docker Compose
docker-compose up -d

# Vérifier que les services sont en cours d'exécution
docker-compose ps
```

**Services démarrés :**
- Backend API : http://localhost:8000
- Documentation API : http://localhost:8000/docs
- PostgreSQL : localhost:5432
- Redis : localhost:6379
- MinIO : http://localhost:9000 (console: http://localhost:9001)

### 2. Frontend (React + Vite)

```bash
# Naviguer vers le répertoire frontend
cd c:\Users\DELL\formbuilder\frontend

# Installer les dépendances (première fois uniquement)
npm install

# Démarrer le serveur de développement
npm run dev
```

**Application accessible sur :** http://localhost:5173

## 🔐 Connexion

### Créer un utilisateur (première fois)

Utilisez l'API pour créer un utilisateur :

```bash
# Via curl (PowerShell)
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"email":"admin@example.com","password":"admin123","nom":"Admin","prenom":"User"}'
```

Ou utilisez la documentation interactive : http://localhost:8000/docs

### Se connecter

1. Ouvrez http://localhost:5173
2. Utilisez les identifiants créés
   - Email : `admin@example.com`
   - Mot de passe : `admin123`

## 📁 Structure du projet

```
formbuilder/
├── formBuilder_backend/    # API FastAPI avec Docker
│   ├── app/               # Code source Python
│   ├── docker-compose.yml # Configuration Docker
│   ├── Dockerfile         # Image Docker du backend
│   └── requirements.txt   # Dépendances Python
│
└── frontend/              # Application React
    ├── src/              # Code source TypeScript
    ├── public/           # Assets statiques
    └── package.json      # Dépendances npm
```

## 🛠️ Commandes utiles

### Backend (Docker)

```bash
# Voir les logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f backend

# Arrêter les services
docker-compose down

# Redémarrer un service
docker-compose restart backend

# Reconstruire après modification du code
docker-compose up -d --build

# Exécuter une commande dans le conteneur backend
docker-compose exec backend bash
```

### Frontend (npm)

```bash
# Installer les dépendances
npm install

# Démarrer en mode développement
npm run dev

# Compiler pour la production
npm run build

# Prévisualiser la version de production
npm run preview

# Vérifier le code (ESLint)
npm run lint
```

## 🔍 Vérification de l'installation

### Backend

```bash
# Vérifier l'API
curl http://localhost:8000/health

# Ou via PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

Résultat attendu : `{"status":"ok"}`

### Frontend

Ouvrez http://localhost:5173 dans votre navigateur. Vous devriez voir la page de connexion.

## 🐛 Résolution des problèmes

### Backend ne démarre pas

1. **Port déjà utilisé**
   ```bash
   # Vérifier les ports
   netstat -ano | findstr :8000
   netstat -ano | findstr :5432
   ```

2. **Docker Desktop non démarré**
   - Lancez Docker Desktop
   - Attendez que l'icône soit verte

3. **Erreur de base de données**
   ```bash
   # Supprimer les volumes et redémarrer
   docker-compose down -v
   docker-compose up -d
   ```

### Frontend ne démarre pas

1. **Dépendances manquantes**
   ```bash
   # Supprimer node_modules et réinstaller
   Remove-Item -Recurse -Force node_modules
   npm install
   ```

2. **Port 5173 déjà utilisé**
   - Arrêtez l'autre processus
   - Ou modifiez le port dans `vite.config.ts`

3. **Erreurs de compilation TypeScript**
   ```bash
   # Nettoyer le cache
   npm run dev -- --force
   ```

### Problèmes de connexion API

1. **CORS errors**
   - Vérifiez que le backend est accessible
   - Le backend autorise déjà `http://localhost:5173`

2. **401 Unauthorized**
   - Effacez le localStorage : `localStorage.clear()`
   - Reconnectez-vous

## 📊 Fonctionnalités disponibles

### Backend API

- ✅ Authentification JWT
- ✅ CRUD Formulaires
- ✅ CRUD Soumissions
- ✅ Gestion des référentiels
- ✅ Export CSV/Excel/PDF
- ✅ Upload de fichiers
- ✅ Audit logging
- ✅ Rate limiting
- ✅ Cache Redis

### Frontend Application

- ✅ Authentification sécurisée
- ✅ Dashboard avec statistiques
- ✅ Liste et filtres des formulaires
- ✅ Éditeur de formulaires drag-and-drop
- ✅ 9 types de champs
- ✅ Configuration des propriétés
- ✅ Publication/dépublication
- ✅ Interface responsive

## 🔗 Liens utiles

- **Backend API** : http://localhost:8000
- **Documentation API (Swagger)** : http://localhost:8000/docs
- **Documentation API (ReDoc)** : http://localhost:8000/redoc
- **Frontend** : http://localhost:5173
- **MinIO Console** : http://localhost:9001

## 📝 Notes importantes

1. **Première exécution** : La base de données sera automatiquement initialisée
2. **Migrations** : Les migrations Alembic sont appliquées au démarrage
3. **Données de test** : Aucune donnée n'est créée par défaut, utilisez l'API pour créer un compte
4. **Fichiers uploadés** : Stockés dans MinIO (S3-compatible)
5. **Logs** : Consultez `docker-compose logs -f` pour le débogage

## 🎯 Prochaines étapes

1. Créez votre premier formulaire via le frontend
2. Ajoutez des champs avec le drag-and-drop
3. Publiez le formulaire
4. Testez la soumission de formulaires
5. Consultez les statistiques dans le dashboard

## 📄 Documentation complète

- Backend : `formBuilder_backend/ReadMe.md`
- Frontend : `frontend/README.md`

---

**Bon développement ! 🚀**
