# 🎯 Import de Référentiel & Génération Automatique de Formulaire

## Fonctionnement

Le système d'import de référentiel a été amélioré pour **générer automatiquement un formulaire éditable** après l'import d'un fichier Excel.

## Flux Complet

```
1. UTILISATEUR importe fichier Excel
   ↓
2. BACKEND parse le fichier Excel
   → Extraction: metadata, sections, fields, options, validations
   ↓
3. BACKEND crée le référentiel en base de données
   → Table: referentiel
   ↓
4. BACKEND génère AUTOMATIQUEMENT un formulaire
   → Conversion: référentiel → structure de formulaire
   → Création dans table: formulaire
   ↓
5. BACKEND retourne la réponse avec:
   - referentiel: données du référentiel importé
   - formulaire_genere: informations du formulaire créé
   ↓
6. FRONTEND reçoit la réponse
   → Détecte formulaire_genere
   → Affiche message de succès
   ↓
7. FRONTEND redirige AUTOMATIQUEMENT
   → URL: /formulaires/{id}
   → L'éditeur FormBuilder s'ouvre
   ↓
8. UTILISATEUR peut éditer le formulaire
   → Modifier les champs
   → Ajouter/supprimer des éléments
   → Publier le formulaire
```

## Exemple de Réponse API

```json
{
  "success": true,
  "message": "Référentiel importé et formulaire #42 généré avec succès",
  "referentiel": {
    "id": 123,
    "version": "1.0.0",
    "metadata": {
      "name": "Formulaire d'inscription",
      "description": "..."
    },
    "config": {
      "sections": [...]
    }
  },
  "formulaire_genere": {
    "id": 42,
    "nom": "Formulaire d'inscription",
    "description": "Importé depuis Excel",
    "publie": false,
    "nb_champs": 15,
    "nb_sections": 3,
    "edit_url": "/formulaires/42"
  },
  "warnings": []
}
```

## Conversion Référentiel → Formulaire

### Types de Champs Supportés

| Type Référentiel | Type Formulaire | Notes |
|-----------------|-----------------|-------|
| text | text | Texte simple |
| textarea | textarea | Texte multiligne |
| email | email | Email avec validation |
| tel | tel | Numéro de téléphone |
| number | number | Nombre |
| date | date | Date |
| datetime-local | datetime | Date et heure |
| time | time | Heure |
| select | select | Liste déroulante |
| multiselect | multiselect | Sélection multiple |
| radio | radio | Boutons radio |
| checkbox | checkbox | Cases à cocher |
| switch | checkbox | Interrupteur → checkbox |
| file | file | Upload de fichier |
| range | range | Curseur |
| color | color | Sélecteur de couleur |
| url | url | URL |
| password | password | Mot de passe |

### Validations Converties

```typescript
// Référentiel
{
  "validation": {
    "required": true,
    "min": 0,
    "max": 100,
    "minLength": 5,
    "maxLength": 255,
    "pattern": "^[A-Z].*"
  }
}

// Formulaire généré
{
  "requis": true,
  "min": 0,
  "max": 100,
  "min_length": 5,
  "max_length": 255,
  "pattern": "^[A-Z].*"
}
```

### Options Converties

```typescript
// Référentiel
{
  "options": [
    { "label": "Option 1", "value": "opt1" },
    { "label": "Option 2", "value": "opt2" }
  ]
}

// Formulaire généré
{
  "options": [
    { "label": "Option 1", "valeur": "opt1" },
    { "label": "Option 2", "valeur": "opt2" }
  ]
}
```

## Paramètres d'Import

### Endpoint: `POST /api/v1/referentiels/import/excel`

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `file` | File | - | Fichier Excel (.xlsx, .xls) **[Requis]** |
| `save_as_template` | bool | false | Sauvegarder comme template public |
| `auto_generate_form` | bool | **true** | Générer automatiquement le formulaire |
| `auto_publish` | bool | false | Publier automatiquement le formulaire |

### Exemples

#### 1. Import Simple (génération auto)
```bash
curl -X POST http://localhost:8001/api/v1/referentiels/import/excel \
  -H "Authorization: Bearer <token>" \
  -F "file=@mon_formulaire.xlsx"
```
✅ Génère automatiquement le formulaire
✅ Redirige vers l'éditeur

#### 2. Import Sans Génération
```bash
curl -X POST http://localhost:8001/api/v1/referentiels/import/excel \
  -H "Authorization: Bearer <token>" \
  -F "file=@mon_formulaire.xlsx" \
  -F "auto_generate_form=false"
```
✅ Importe seulement le référentiel
❌ Pas de formulaire généré

#### 3. Import et Publication
```bash
curl -X POST http://localhost:8001/api/v1/referentiels/import/excel \
  -H "Authorization: Bearer <token>" \
  -F "file=@mon_formulaire.xlsx" \
  -F "auto_generate_form=true" \
  -F "auto_publish=true"
```
✅ Génère le formulaire
✅ Publie immédiatement
✅ Redirige vers l'éditeur

## Structure Excel Requise

Votre fichier Excel doit contenir ces feuilles :

### 1. **Metadata** (Informations globales)
| Champ | Valeur |
|-------|--------|
| name | Nom du formulaire |
| description | Description |
| version | 1.0.0 |
| author | Votre nom |

### 2. **Sections** (Organisation)
| id | title | description | order |
|----|-------|-------------|-------|
| section1 | Informations | ... | 1 |
| section2 | Contact | ... | 2 |

### 3. **Fields** (Champs)
| section_id | group_id | field_id | type | label | required |
|------------|----------|----------|------|-------|----------|
| section1 | group1 | nom | text | Nom | true |
| section1 | group1 | email | email | Email | true |

### 4. **Options** (Pour select/radio/checkbox)
| field_id | value | label | order |
|----------|-------|-------|-------|
| pays | fr | France | 1 |
| pays | be | Belgique | 2 |

### 5. **Validation** (Règles)
| field_id | rule | value | message |
|----------|------|-------|---------|
| email | pattern | ^[\w.-]+@[\w.-]+\.\w+$ | Email invalide |
| age | min | 18 | Vous devez avoir au moins 18 ans |

## Utilisation dans l'Interface

### Étapes

1. **Cliquez sur "Formulaires Dynamiques"** dans le menu
2. **Cliquez sur "Importer un référentiel"**
3. **Sélectionnez votre fichier Excel**
4. **Attendez le traitement** (~quelques secondes)
5. **Message de confirmation** s'affiche avec statistiques
6. **Redirection automatique** vers l'éditeur
7. **Éditez votre formulaire** dans FormBuilder

### Message de Succès

```
✅ Formulaire "Inscription Événement" créé avec succès !

📊 15 champs dans 3 sections

🔄 Redirection vers l'éditeur...
```

## Génération Manuelle (Alternative)

Si vous avez déjà importé un référentiel sans génération automatique :

```bash
POST /api/v1/referentiels/{referentiel_id}/generate-form
```

Paramètres :
- `auto_publish`: Publier immédiatement (défaut: false)

Réponse :
```json
{
  "success": true,
  "message": "Formulaire généré avec succès",
  "formulaire": {
    "id": 42,
    "nom": "...",
    "edit_url": "/formulaires/42"
  }
}
```

## Dépannage

### Le formulaire ne se génère pas

**Vérifications :**
1. Le fichier Excel est-il bien formaté ?
2. Contient-il les feuilles requises (Metadata, Sections, Fields) ?
3. Les champs ont-ils des types valides ?
4. Y a-t-il au moins 1 section avec 1 champ ?

**Logs à vérifier :**
```
Backend:
📤 IMPORT EXCEL - Début du traitement
✅ REFERENTIEL CRÉÉ EN BASE
🏗️  GÉNÉRATION AUTOMATIQUE DU FORMULAIRE
✅ FORMULAIRE GÉNÉRÉ AUTOMATIQUEMENT

Frontend:
📥 Réponse complète reçue
🎉 FORMULAIRE GÉNÉRÉ AUTOMATIQUEMENT !
```

### La redirection ne fonctionne pas

**Causes possibles :**
1. `auto_generate_form` est à `false`
2. Erreur lors de la génération
3. Permission insuffisante

**Solution :**
- Vérifiez les logs de la console (F12)
- Vérifiez que `response.data.formulaire_genere` existe
- Vérifiez votre token d'authentification

## Avantages

✅ **Automatique** - Pas de manipulation manuelle
✅ **Rapide** - Génération en quelques secondes  
✅ **Éditable** - Formulaire modifiable dans FormBuilder
✅ **Traçable** - Lien vers le référentiel source conservé
✅ **Flexible** - Options de publication configurables

---

**Dernière mise à jour :** 20 décembre 2025
