# 🌍 Guide d'utilisation de l'internationalisation (i18n)

## ✅ Configuration actuelle

L'application supporte maintenant **2 langues** :
- 🇫🇷 **Français** (par défaut)
- 🇬🇧 **Anglais**

## 🎯 Comment ça fonctionne

### 1. Changement de langue

Le **LanguageSwitcher** est dans le header de l'application :
- Cliquer sur le menu déroulant à côté de l'icône 🌐
- Sélectionner "Français" ou "English"
- **La langue change immédiatement** sur la page de connexion
- **La préférence est sauvegardée** dans le navigateur

### 2. Pages traduites actuellement

✅ **LoginPage** - Page de connexion entièrement traduite :
- Titre de l'application
- Description ("Connectez-vous à votre compte" / "Sign in to your account")
- Labels des champs (Email, Mot de passe)
- Placeholders
- Boutons (Se connecter / Sign in)
- Liens (Mot de passe oublié, Créer un compte)
- Messages d'erreur

### 3. Test rapide

**Pour tester le changement de langue :**

1. Aller sur la page de connexion : `http://localhost:5173/login`
2. Observer le texte en français par défaut
3. Cliquer sur le sélecteur de langue en haut à droite
4. Sélectionner "English"
5. **Résultat** :
   - "Connectez-vous à votre compte" → "Sign in to your account"
   - "Se connecter" → "Sign in"
   - "Pas encore de compte ?" → "Don't have an account?"
   - "S'inscrire" → "Sign up"

## 📂 Fichiers de traduction

**Français** : `frontend/src/i18n/locales/fr.json`
**Anglais** : `frontend/src/i18n/locales/en.json`

### Structure des traductions

```json
{
  "app": {
    "title": "FormBuilder"
  },
  "auth": {
    "email": "Email",
    "password": "Mot de passe",
    "loginButton": "Se connecter",
    "loginDescription": "Connectez-vous à votre compte",
    "forgotPassword": "Mot de passe oublié ?",
    "noAccount": "Pas encore de compte ?",
    "registerButton": "S'inscrire"
  }
}
```

## 🔧 Comment ajouter des traductions à d'autres pages

### Étape 1 : Importer useTranslation

```tsx
import { useTranslation } from 'react-i18next';

export const MaPage = () => {
  const { t } = useTranslation();
  // ...
```

### Étape 2 : Remplacer le texte par des clés de traduction

```tsx
// Avant
<h1>Tableau de bord</h1>

// Après
<h1>{t('dashboard.title')}</h1>
```

### Étape 3 : Ajouter les traductions dans les fichiers JSON

**fr.json** :
```json
{
  "dashboard": {
    "title": "Tableau de bord"
  }
}
```

**en.json** :
```json
{
  "dashboard": {
    "title": "Dashboard"
  }
}
```

## 🎨 Traductions disponibles

### App
- `app.title` → "FormBuilder"
- `app.description` → Description de l'application

### Auth (Authentification)
- `auth.login` → "Connexion" / "Login"
- `auth.email` → "Email"
- `auth.password` → "Mot de passe" / "Password"
- `auth.loginButton` → "Se connecter" / "Sign in"
- `auth.registerButton` → "S'inscrire" / "Sign up"
- `auth.forgotPassword` → "Mot de passe oublié ?" / "Forgot password?"
- `auth.noAccount` → "Pas encore de compte ?" / "Don't have an account?"
- `auth.invalidCredentials` → Message d'erreur

### Dashboard
- `dashboard.title` → "Tableau de bord" / "Dashboard"
- `dashboard.totalForms` → "Total Formulaires" / "Total Forms"
- `dashboard.publishedForms` → "Formulaires Publiés" / "Published Forms"
- `dashboard.totalSubmissions` → "Total Soumissions" / "Total Submissions"

### Forms
- `forms.create` → "Créer un formulaire" / "Create Form"
- `forms.edit` → "Modifier" / "Edit"
- `forms.delete` → "Supprimer" / "Delete"
- `forms.preview` → "Aperçu" / "Preview"
- `forms.export` → "Exporter" / "Export"

### Fields (Types de champs)
- `forms.fields.text` → "Texte" / "Text"
- `forms.fields.email` → "Email"
- `forms.fields.number` → "Nombre" / "Number"
- `forms.fields.geolocation` → "Géolocalisation" / "Geolocation"
- `forms.fields.signature` → "Signature"

### Common
- `common.save` → "Enregistrer" / "Save"
- `common.cancel` → "Annuler" / "Cancel"
- `common.delete` → "Supprimer" / "Delete"
- `common.confirm` → "Confirmer" / "Confirm"
- `common.loading` → "Chargement..." / "Loading..."

## 🚀 Prochaines étapes recommandées

Pour étendre l'i18n à toute l'application :

1. **Dashboard** - Traduire les statistiques et graphiques
2. **FormBuilder** - Traduire la palette de champs et les propriétés
3. **FormulairesList** - Traduire les colonnes du tableau
4. **Soumissions** - Traduire les statuts et filtres
5. **Settings** - Traduire les paramètres utilisateur

## 🐛 Dépannage

### La langue ne change pas

**Vérifications** :
1. ✅ Le fichier `frontend/src/i18n/config.ts` existe
2. ✅ Import dans `main.tsx` : `import './i18n/config'`
3. ✅ Le composant utilise `useTranslation()`
4. ✅ Les clés de traduction existent dans `fr.json` et `en.json`

**Solution** :
- Vérifier la console du navigateur pour les erreurs
- Recharger la page avec Ctrl+Shift+R (hard refresh)
- Vider le localStorage : `localStorage.clear()`

### Clé de traduction manquante

Si vous voyez la clé affichée au lieu du texte (ex: `auth.loginButton`) :

1. Vérifier que la clé existe dans **les deux** fichiers (`fr.json` et `en.json`)
2. Respecter la casse et les points : `auth.loginButton` ≠ `Auth.loginButton`
3. Redémarrer le serveur de développement

## 📝 Exemple complet

```tsx
import { useTranslation } from 'react-i18next';

export const MonComposant = () => {
  const { t, i18n } = useTranslation();
  
  // Afficher une traduction
  return (
    <div>
      <h1>{t('app.title')}</h1>
      <p>{t('dashboard.welcome', { name: 'John' })}</p>
      
      {/* Langue actuelle */}
      <p>Langue: {i18n.language}</p>
      
      {/* Changer de langue programmatiquement */}
      <button onClick={() => i18n.changeLanguage('en')}>
        English
      </button>
    </div>
  );
};
```

## 🎯 Résultat attendu

**Avant (texte en dur)** :
```tsx
<h1>Connectez-vous à votre compte</h1>
<button>Se connecter</button>
```

**Après (traduit)** :
```tsx
<h1>{t('auth.loginDescription')}</h1>
<button>{t('auth.loginButton')}</button>
```

**Résultat visuel** :
- 🇫🇷 FR : "Connectez-vous à votre compte" + "Se connecter"
- 🇬🇧 EN : "Sign in to your account" + "Sign in"

---

✅ **L'internationalisation fonctionne maintenant sur la page de connexion !**

**Pour voir le changement** : Allez sur `/login` et changez la langue avec le sélecteur en haut à droite.
