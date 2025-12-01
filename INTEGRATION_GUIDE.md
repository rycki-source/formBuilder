# 🔗 Guide d'Intégration - FormBuilder

## Vue d'ensemble

Ce guide vous explique comment **intégrer les formulaires FormBuilder dans votre site web existant**.

## 🚀 Méthode rapide (5 minutes)

### Étape 1 : Créer votre formulaire

1. Connectez-vous à FormBuilder : `http://localhost:5173`
2. Créez un formulaire avec les champs souhaités
3. Publiez le formulaire

### Étape 2 : Récupérer le code d'intégration

1. Allez sur "Aperçu" du formulaire
2. Cliquez sur le bouton **"Code"**
3. **Copiez** tout le code affiché

### Étape 3 : Intégrer dans votre site

Collez le code copié dans votre page HTML :

```html
<!DOCTYPE html>
<html>
<head>
    <title>Ma Page</title>
</head>
<body>
    <h1>Mon Site Web</h1>
    
    <!-- COLLEZ LE CODE ICI -->
    
</body>
</html>
```

**C'est tout !** Le formulaire est maintenant fonctionnel sur votre site. ✅

---

## 📋 Ce que le code fait automatiquement

✅ Affiche le formulaire avec tous vos champs  
✅ Valide les champs obligatoires  
✅ Soumet les données à votre API FormBuilder  
✅ Affiche un message de succès/erreur  
✅ Réinitialise le formulaire après soumission  

---

## 🎨 Personnalisation

### Modifier les couleurs

Le code contient une section `<style>`. Modifiez les couleurs :

```css
/* Couleur primaire (boutons) */
.button-primary {
    background-color: #10b981; /* Vert au lieu de bleu */
}

/* Couleur de fond */
.formbuilder-container {
    background-color: #f9fafb;
}
```

### Modifier l'URL de l'API

Si votre API n'est pas sur `localhost:8000`, modifiez :

```javascript
const API_BASE_URL = 'https://mon-api.com/api/v1';
```

### Supprimer le titre

Supprimez ou commentez ces lignes dans le code :

```html
<!-- Supprimez cette section -->
<div class="formbuilder-header">
    <h2>Nom du formulaire</h2>
    ...
</div>
```

---

## 🔒 Configuration CORS (Important !)

Pour que le formulaire puisse envoyer des données depuis votre site, configurez CORS sur votre backend.

### Fichier : `formBuilder_backend/app/main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://mon-site.com",  # Ajoutez votre domaine ici
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Récupérer les soumissions

### Via l'interface

1. Allez sur "Formulaires"
2. Cliquez sur "Soumissions" du formulaire
3. Consultez toutes les réponses

### Via l'API

```bash
# Récupérer toutes les soumissions d'un formulaire
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/soumissions?formulaire_id=1
```

```javascript
// Avec JavaScript
const response = await fetch('http://localhost:8000/api/v1/soumissions?formulaire_id=1', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});
const soumissions = await response.json();
```

---

## 💡 Exemples d'intégration

### Dans WordPress

Utilisez un bloc HTML personnalisé :

1. Éditeur → Ajouter un bloc → HTML personnalisé
2. Collez le code du formulaire
3. Publiez la page

### Dans React

```jsx
import { useEffect } from 'react';

function MonComposant() {
  useEffect(() => {
    // Charger le code du formulaire
    fetch('http://localhost:8000/api/v1/formulaires/1/embed')
      .then(res => res.text())
      .then(html => {
        document.getElementById('form-container').innerHTML = html;
      });
  }, []);

  return <div id="form-container"></div>;
}
```

### Dans Vue.js

```vue
<template>
  <div v-html="formHtml"></div>
</template>

<script>
export default {
  data() {
    return {
      formHtml: ''
    }
  },
  mounted() {
    fetch('http://localhost:8000/api/v1/formulaires/1/embed')
      .then(res => res.text())
      .then(html => {
        this.formHtml = html;
      });
  }
}
</script>
```

### Dans une page statique

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Contact</title>
</head>
<body>
    <header>
        <nav>
            <a href="/">Accueil</a>
            <a href="/contact.html">Contact</a>
        </nav>
    </header>
    
    <main style="max-width: 800px; margin: 0 auto; padding: 40px 20px;">
        <h1>Contactez-nous</h1>
        <p>Remplissez le formulaire ci-dessous et nous vous répondrons rapidement.</p>
        
        <!-- Formulaire FormBuilder -->
        <div id="contact-form">
            <!-- Collez ici le code récupéré avec le bouton "Code" -->
        </div>
    </main>
    
    <footer>
        <p>&copy; 2025 Mon Entreprise</p>
    </footer>
</body>
</html>
```

---

## 🎯 Cas d'usage courants

### 1. Formulaire de contact

```
Champs : Nom, Email, Message
Type : Simple
Utilisation : Page de contact du site
```

### 2. Inscription événement

```
Champs : Nom, Email, Téléphone, Nombre de participants
Type : Simple ou Multi-étapes
Utilisation : Landing page événement
```

### 3. Commande personnalisée

```
Champs : Produit, Quantité, Options, Coordonnées, Livraison
Type : Multi-étapes (wizard)
Utilisation : Boutique en ligne
```

### 4. Candidature emploi

```
Champs : CV (file), Lettre motivation, Expérience, Formation
Type : Multi-étapes
Utilisation : Page carrières
```

---

## 🔧 Dépannage

### Le formulaire ne s'affiche pas

**Vérifiez :**
- Le code est bien copié dans une balise `<div>` ou `<section>`
- La console du navigateur (F12) pour les erreurs JavaScript
- Que votre éditeur n'a pas échappé les balises HTML

### "Erreur de connexion au serveur"

**Vérifiez :**
- L'API backend est démarrée : `http://localhost:8000/docs`
- L'URL dans `API_BASE_URL` est correcte
- CORS est configuré pour votre domaine
- Pas de bloqueur de publicités/scripts

### Les données ne sont pas envoyées

**Vérifiez :**
- Les attributs `name` sur les champs (générés automatiquement)
- La console réseau (F12 → Network) pour voir la requête
- Le format JSON envoyé est correct
- L'endpoint `/soumissions` est accessible

### Problème de style

**Solution :**
- Les styles sont dans une balise `<style>` au début du code
- Vérifiez qu'il n'y a pas de conflit avec vos CSS existants
- Ajoutez `!important` si nécessaire
- Encapsulez dans un conteneur avec classe unique

---

## 📱 Responsive Design

Le formulaire est automatiquement responsive :

- **Desktop** : Colonnes et espacement large
- **Tablette** : Ajustement automatique
- **Mobile** : Une colonne, tactile-friendly

Aucune configuration nécessaire ! ✅

---

## 🚀 Passage en production

### Checklist avant déploiement

- [ ] Tester le formulaire localement
- [ ] Configurer CORS avec votre domaine de production
- [ ] Modifier `API_BASE_URL` vers votre API de production
- [ ] Tester depuis votre site de production
- [ ] Configurer HTTPS pour l'API (recommandé)
- [ ] Mettre en place un rate limiting
- [ ] Tester la réception des soumissions

### Exemple configuration production

```javascript
// Dans le code embarquable
const API_BASE_URL = 'https://api.mon-entreprise.com/api/v1';
```

```python
# Backend CORS
allow_origins=[
    "https://www.mon-site.com",
    "https://mon-site.com",
]
```

---

## 📖 Ressources supplémentaires

- **Documentation complète** : `EXPORT_FORMULAIRES.md`
- **API Reference** : `http://localhost:8000/docs`
- **Support** : [Votre email/support]

---

## 💬 Besoin d'aide ?

Si vous rencontrez des difficultés :

1. Consultez la console du navigateur (F12)
2. Vérifiez les logs backend
3. Testez l'API directement avec la doc : `http://localhost:8000/docs`
4. Consultez `EXPORT_FORMULAIRES.md` pour plus de détails

---

**Bonne intégration ! 🎉**
