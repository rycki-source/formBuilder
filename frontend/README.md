# FormBuilder Frontend

Application React + TypeScript pour la création et gestion de formulaires dynamiques avec un éditeur drag-and-drop.

## 🚀 Technologies utilisées

- **React 18** - Bibliothèque UI
- **TypeScript** - Typage statique
- **Vite 7** - Build tool et dev server rapide
- **TailwindCSS 4** - Framework CSS utility-first
- **React Router 7** - Gestion du routing
- **Zustand 5** - State management léger
- **React Hook Form** - Gestion des formulaires
- **@dnd-kit** - Drag-and-drop pour l'éditeur de formulaires
- **Axios** - Client HTTP
- **Lucide React** - Icônes

## 📦 Installation

```bash
# Installer les dépendances
npm install
```

## 🏃 Lancer l'application

```bash
# Mode développement
npm run dev

# Compiler pour la production
npm run build

# Prévisualiser la version de production
npm run preview
```

L'application sera accessible sur [http://localhost:5173](http://localhost:5173)

## 🔑 Configuration

Assurez-vous que le backend API est en cours d'exécution sur `http://localhost:8000`

Si vous devez changer l'URL de l'API, modifiez la constante `API_BASE_URL` dans :
```typescript
src/api/axios.ts
```

## 📁 Structure du projet

```
src/
├── api/              # Clients API et axios config
│   ├── axios.ts      # Configuration axios avec intercepteurs JWT
│   ├── auth.ts       # API d'authentification
│   ├── formulaires.ts # API de gestion des formulaires
│   └── soumissions.ts # API de gestion des soumissions
│
├── components/       # Composants réutilisables
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Input.tsx
│   ├── Layout.tsx
│   └── ProtectedRoute.tsx
│
├── features/         # Composants liés à des fonctionnalités
│   └── FormBuilder/
│       ├── FieldEditor.tsx   # Éditeur de propriétés de champ
│       ├── FieldList.tsx     # Liste drag-and-drop des champs
│       └── FieldPalette.tsx  # Palette des types de champs
│
├── hooks/            # Hooks personnalisés
│   └── useAuth.ts    # Hook d'authentification
│
├── pages/            # Pages de l'application
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   ├── FormListPage.tsx
│   └── FormBuilderPage.tsx
│
├── store/            # State management (Zustand)
│   ├── authStore.ts        # Store d'authentification
│   └── formBuilderStore.ts # Store de gestion des formulaires
│
├── types/            # Types TypeScript
│   └── index.ts      # Interfaces et types
│
└── utils/            # Fonctions utilitaires
```

## 🎨 Fonctionnalités

### Authentification
- Page de connexion sécurisée
- Gestion des tokens JWT dans localStorage
- Routes protégées avec redirection automatique
- Récupération automatique de la session

### Tableau de bord
- Vue d'ensemble des formulaires
- Statistiques en temps réel
- Accès rapide aux fonctionnalités
- Formulaires récents

### Gestion des formulaires
- Liste complète avec filtres (tous, publiés, brouillons)
- Carte de présentation pour chaque formulaire
- Actions rapides : éditer, aperçu, publier/dépublier, supprimer
- Compteur de champs par formulaire

### Éditeur de formulaires (Form Builder)

**9 types de champs disponibles :**
- ✏️ Texte
- 📧 Email
- 🔢 Nombre
- 📅 Date
- 📋 Liste déroulante
- 📝 Zone de texte
- ☑️ Case à cocher
- ⭕ Bouton radio
- 📁 Fichier

**Fonctionnalités de l'éditeur :**
- Drag-and-drop pour réorganiser les champs
- Éditeur de propriétés en temps réel
  - Label personnalisable
  - Placeholder
  - Champ obligatoire
  - Options (pour select et radio)
- Sauvegarde manuelle
- Prévisualisation

## 🔒 Sécurité

- Token JWT stocké dans localStorage
- Intercepteur Axios pour ajouter automatiquement le token
- Gestion automatique de l'expiration (redirection 401)
- Routes protégées avec composant ProtectedRoute

## 🎯 Routes

| Route | Description | Protection |
|-------|-------------|------------|
| `/login` | Page de connexion | Publique |
| `/dashboard` | Tableau de bord | Protégée |
| `/formulaires` | Liste des formulaires | Protégée |
| `/formulaires/nouveau` | Créer un formulaire | Protégée |
| `/formulaires/:id` | Éditer un formulaire | Protégée |
| `/` | Redirection vers dashboard | - |

## 📝 API Backend

Communication avec le backend FastAPI via `http://localhost:8000/api/v1`

### Endpoints d'authentification
```
POST /auth/login           # Connexion (form-data: username, password)
GET  /auth/me              # Récupérer l'utilisateur connecté
```

### Endpoints des formulaires
```
GET    /formulaires             # Liste des formulaires
GET    /formulaires/:id         # Détails d'un formulaire
POST   /formulaires             # Créer un formulaire
PUT    /formulaires/:id         # Modifier un formulaire
DELETE /formulaires/:id         # Supprimer un formulaire
POST   /formulaires/:id/publier # Publier un formulaire
POST   /formulaires/:id/depublier # Dépublier un formulaire
```

### Endpoints des soumissions
```
GET  /soumissions              # Liste des soumissions
GET  /soumissions/:id          # Détails d'une soumission
POST /soumissions              # Créer une soumission
PUT  /soumissions/:id/statut   # Modifier le statut
```

## 🛠️ Scripts disponibles

```bash
npm run dev      # Serveur de développement (http://localhost:5173)
npm run build    # Compilation pour la production
npm run preview  # Prévisualisation de la version compilée
npm run lint     # Vérification ESLint du code
```

## 📦 Dépendances principales

```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "react-router-dom": "^7.1.1",
  "zustand": "^5.0.2",
  "axios": "^1.7.9",
  "react-hook-form": "^7.54.2",
  "@hookform/resolvers": "^3.9.1",
  "zod": "^3.24.1",
  "@dnd-kit/core": "^6.3.1",
  "@dnd-kit/sortable": "^9.0.0",
  "lucide-react": "^0.468.0",
  "tailwindcss": "^4.0.6"
}
```

## 🎨 Personnalisation

### Thème TailwindCSS
Modifiez `tailwind.config.js` pour personnaliser :
- Couleurs (primaire, secondaire, etc.)
- Espacements
- Polices
- Breakpoints responsive

### Composants UI
Les composants de base sont dans `src/components/` :
- `Button.tsx` - 4 variantes (primary, secondary, danger, outline)
- `Input.tsx` - Input avec label et validation
- `Card.tsx` - Conteneur avec titre et action

## 🐛 Débogage

1. **Erreurs de connexion API**
   - Vérifiez que le backend est démarré sur http://localhost:8000
   - Consultez la console navigateur (F12)
   - Vérifiez les erreurs réseau dans l'onglet Network

2. **Erreurs d'authentification**
   - Effacez le localStorage : `localStorage.clear()`
   - Reconnectez-vous

3. **Erreurs de rendu**
   - Utilisez React DevTools
   - Inspectez les stores Zustand
   - Vérifiez les props des composants

## 🚀 Déploiement

### Build de production
```bash
npm run build
```

Le dossier `dist/` contiendra l'application compilée.

### Serveur statique
Vous pouvez servir le dossier `dist/` avec n'importe quel serveur HTTP statique :

```bash
# Avec serve
npx serve dist

# Avec http-server
npx http-server dist
```

### Variables d'environnement
Pour un déploiement en production, créez un fichier `.env.production` :

```env
VITE_API_URL=https://votre-backend.com/api/v1
```

Et modifiez `src/api/axios.ts` :
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
```

## 📄 Licence

Projet FormBuilder - Backend FastAPI + Frontend React
