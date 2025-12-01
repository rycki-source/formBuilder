# 📄 Export et Intégration de Formulaires

## Vue d'ensemble

Le système permet maintenant d'exporter et d'intégrer les formulaires créés en trois formats :
- **CODE EMBARQUABLE** : Code HTML + JavaScript prêt à intégrer dans votre site web (RECOMMANDÉ)
- **HTML** : Page HTML standalone complète
- **PDF** : Document PDF pour impression ou partage

## 🔌 Endpoints API

### 1. **Code embarquable (RECOMMANDÉ pour intégration)**

```http
GET /api/v1/formulaires/{formulaire_id}/embed
```

**Réponse :** Code HTML + JavaScript prêt à intégrer dans votre site

**Ce code inclut :**
- ✅ HTML du formulaire avec tous les champs
- ✅ Styles CSS intégrés
- ✅ JavaScript pour soumettre les données à l'API
- ✅ Validation des champs
- ✅ Gestion des erreurs
- ✅ Attributs `name` et `id` sur tous les champs

**Exemple avec curl :**
```bash
curl http://localhost:8000/api/v1/formulaires/1/embed
```

**Exemple avec PowerShell :**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/formulaires/1/embed" `
  -Method GET `
  -OutFile "formulaire-embed.html"
```

### 2. Récupérer le formulaire en HTML complet

```http
GET /api/v1/formulaires/{formulaire_id}/html
```

**Réponse :** Page HTML standalone complète

**Exemple avec curl :**
```bash
curl http://localhost:8000/api/v1/formulaires/1/html > formulaire.html
```

### 3. Télécharger le formulaire en PDF

```http
GET /api/v1/formulaires/{formulaire_id}/pdf
```

**Réponse :** Fichier PDF téléchargeable

**Exemple avec curl :**
```bash
curl -O -J http://localhost:8000/api/v1/formulaires/1/pdf
```

**Exemple avec PowerShell :**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/formulaires/1/pdf" `
  -Method GET `
  -Headers @{"Authorization"="Bearer VOTRE_TOKEN"} `
  -OutFile "formulaire.pdf"
```

## 🎨 Fonctionnalités du HTML généré

### Design moderne et responsive
- ✅ Styles CSS intégrés (pas de dépendances externes)
- ✅ Design professionnel avec couleurs et espacements optimisés
- ✅ Responsive (s'adapte aux mobiles et tablettes)
- ✅ Prêt à l'emploi : ouvrez le fichier HTML dans un navigateur

### Support de tous les types de formulaires

#### Formulaires simples
```
- Tous les champs affichés sur une seule page
- Boutons de soumission et réinitialisation
```

#### Formulaires multi-étapes et Wizard
```
- Étapes organisées avec titres et descriptions
- Numérotation des étapes (Étape 1, Étape 2, etc.)
- Regroupement visuel des champs par étape
```

#### Formulaires intégrés et Modal
```
- Affichage standard pour intégration dans une page existante
- Le mode modal est représenté comme un formulaire standard dans l'export
```

### Support de tous les types de champs

| Type de champ | Rendu HTML |
|--------------|------------|
| **Texte** | `<input type="text">` avec placeholder |
| **Email** | `<input type="email">` avec validation native |
| **Nombre** | `<input type="number">` |
| **Date** | `<input type="date">` avec sélecteur natif |
| **Select** | `<select>` avec toutes les options |
| **Textarea** | `<textarea>` multiligne |
| **Checkbox** | `<input type="checkbox">` |
| **Radio** | Groupe de `<input type="radio">` |
| **Fichier** | `<input type="file">` |
| **Bouton** | `<button>` avec type et style configurables |

### Gestion des champs obligatoires
- ✅ Marqueur visuel rouge `*` pour les champs requis
- ✅ Attribut HTML `required` pour validation native du navigateur
- ✅ Messages d'erreur automatiques du navigateur

## 🖨️ Fonctionnalités du PDF

### Génération haute qualité
- ✅ Conversion HTML → PDF via WeasyPrint
- ✅ Préservation des styles et mise en page
- ✅ Qualité d'impression professionnelle
- ✅ Nom de fichier automatique : `formulaire_{id}_{nom}.pdf`

### Cas d'usage
- 📋 Documentation de formulaire
- 📧 Partage par email
- 🖨️ Impression papier
- 📁 Archivage
- 📱 Consultation hors ligne

## 💻 Utilisation dans le Frontend

### Interface utilisateur

Dans la page **Aperçu du formulaire** (`/formulaires/{id}/preview`), trois boutons sont disponibles :

1. **Bouton CODE** (icône code) - **RECOMMANDÉ**
   - Affiche le code HTML + JavaScript embarquable
   - Prêt à copier-coller dans votre site
   - Inclut la soumission automatique vers l'API
   - Modal avec exemple d'intégration

2. **Bouton HTML** (icône document)
   - Télécharge une page HTML complète standalone
   - Nom du fichier : `formulaire_{nom}.html`
   - Peut être ouvert directement dans un navigateur

3. **Bouton PDF** (icône téléchargement)
   - Génère et télécharge le PDF
   - Nom du fichier : `formulaire_{nom}.pdf`
   - Prêt pour impression ou partage

## 🔗 Intégration dans votre site web

### Méthode 1 : Via l'interface (Recommandé)

1. **Ouvrir** le formulaire dans FormBuilder
2. **Cliquer** sur "Aperçu"
3. **Cliquer** sur le bouton "Code"
4. **Copier** le code affiché
5. **Coller** dans votre page HTML

### Méthode 2 : Via l'API

```javascript
// Récupérer le code embarquable
fetch('http://localhost:8000/api/v1/formulaires/1/embed')
  .then(response => response.text())
  .then(html => {
    // Injecter dans votre page
    document.getElementById('form-container').innerHTML = html;
  });
```

### Exemple d'intégration complète

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mon Site avec Formulaire</title>
</head>
<body>
    <header>
        <h1>Bienvenue sur mon site</h1>
    </header>
    
    <main>
        <section>
            <h2>Contactez-nous</h2>
            <p>Remplissez ce formulaire pour nous contacter.</p>
            
            <!-- COLLEZ ICI LE CODE EMBARQUABLE -->
            <div id="form-container">
                <!-- Le code du formulaire va ici -->
            </div>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2025 Mon Site</p>
    </footer>
</body>
</html>
```

### Configuration de l'API

Le code embarquable utilise par défaut `http://localhost:8000/api/v1`. Pour modifier l'URL de l'API :

```javascript
// Dans le code embarquable, modifiez cette ligne :
const API_BASE_URL = 'https://votre-api.com/api/v1';  // Votre URL de production
```

### Fonctionnement du formulaire embarqué

1. **Affichage** : Le formulaire s'affiche avec tous ses champs et styles
2. **Validation** : Validation HTML5 native des champs obligatoires
3. **Soumission** : Au clic sur "Soumettre" :
   - Les données sont collectées automatiquement
   - Envoi vers `POST /api/v1/soumissions`
   - Affichage d'un message de succès ou d'erreur
   - Réinitialisation du formulaire si succès

### Données envoyées à l'API

```json
{
  "formulaire_id": 1,
  "donnees": {
    "nom": "Dupont",
    "email": "dupont@example.com",
    "message": "Bonjour...",
    "accepte_conditions": true
  }
}
```

### Code d'intégration

```typescript
// Télécharger le HTML
const handleDownloadHTML = async () => {
  const response = await apiClient.get(`/formulaires/${id}/html`, {
    responseType: 'text'
  });
  
  const blob = new Blob([response.data], { type: 'text/html' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'formulaire.html';
  link.click();
};

// Télécharger le PDF
const handleDownloadPDF = async () => {
  const response = await apiClient.get(`/formulaires/${id}/pdf`, {
    responseType: 'blob'
  });
  
  const blob = new Blob([response.data], { type: 'application/pdf' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'formulaire.pdf';
  link.click();
};
```

## 🎨 Personnalisation du HTML

### Structure générée

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Nom du formulaire</title>
    <style>
        /* Styles CSS intégrés */
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Nom du formulaire</h1>
            <span class="badge">Type</span>
            <p class="description">Description</p>
        </div>
        
        <form>
            <!-- Champs du formulaire -->
        </form>
        
        <div class="footer">
            Généré par FormBuilder
        </div>
    </div>
</body>
</html>
```

### Modification des styles

Le HTML généré contient des styles CSS dans une balise `<style>`. Vous pouvez :

1. **Télécharger le HTML**
2. **Ouvrir avec un éditeur de texte**
3. **Modifier les styles CSS** dans la section `<style>`
4. **Personnaliser les couleurs, polices, espacements, etc.**

Exemples de personnalisation :

```css
/* Changer la couleur primaire */
.button-primary {
    background-color: #10b981; /* Vert au lieu de bleu */
}

/* Changer la police */
body {
    font-family: 'Georgia', serif;
}

/* Modifier la largeur du conteneur */
.container {
    max-width: 1000px; /* Au lieu de 800px */
}
```

## 🔧 Configuration Backend

### Dépendances requises

Le fichier `requirements.txt` inclut déjà :
```
weasyprint==60.1
```

### Installation (si nécessaire)

```bash
pip install weasyprint
```

**Note :** WeasyPrint peut nécessiter des dépendances système :
- **Windows** : Généralement pas de dépendances supplémentaires
- **Linux** : `python3-dev python3-cffi libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0`
- **macOS** : `brew install cairo pango gdk-pixbuf`

## 📊 Exemples d'utilisation

### 1. Export pour intégration web

```bash
# Télécharger le HTML
curl http://localhost:8000/api/v1/formulaires/1/html > formulaire.html

# Intégrer dans votre site
<iframe src="formulaire.html" width="100%" height="600"></iframe>
```

### 2. Export pour documentation

```bash
# Générer PDF de tous les formulaires
for id in {1..10}; do
  curl -O -J "http://localhost:8000/api/v1/formulaires/$id/pdf"
done
```

### 3. Export programmatique (Python)

```python
import requests

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "votre_token_jwt"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Télécharger HTML
response = requests.get(f"{BASE_URL}/formulaires/1/html", headers=headers)
with open("formulaire.html", "w", encoding="utf-8") as f:
    f.write(response.text)

# Télécharger PDF
response = requests.get(f"{BASE_URL}/formulaires/1/pdf", headers=headers)
with open("formulaire.pdf", "wb") as f:
    f.write(response.content)
```

## 🚀 Cas d'usage avancés

### 1. Envoi par email

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Générer le PDF
pdf_bytes = PDFGenerator.generate_from_html(html_content)

# Créer l'email
msg = MIMEMultipart()
msg['Subject'] = 'Formulaire à remplir'

# Attacher le PDF
attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
attachment.add_header('Content-Disposition', 'attachment', filename='formulaire.pdf')
msg.attach(attachment)

# Envoyer
smtp.send_message(msg)
```

### 2. Stockage dans MinIO/S3

```python
# Uploader le PDF dans MinIO
pdf_bytes = PDFGenerator.generate_from_html(html_content)
s3_client.put_object(
    Bucket='formulaires',
    Key=f'formulaire_{id}.pdf',
    Body=pdf_bytes,
    ContentType='application/pdf'
)
```

### 3. API de partage public

```python
# Créer un endpoint public (sans authentification)
@router.get("/formulaires/{id}/public/pdf")
async def get_public_pdf(id: int):
    # Vérifier que le formulaire est publié
    if not formulaire.publie:
        raise HTTPException(404)
    
    return generate_pdf(formulaire)
```

## 🔒 Sécurité

### Contrôle d'accès
- ✅ Authentification JWT requise par défaut
- ✅ Seuls les utilisateurs connectés peuvent exporter
- ✅ Possibilité d'ajouter des permissions par rôle

### Recommandations
- 🔐 Limiter l'export aux formulaires publiés pour les utilisateurs non-admin
- 🔐 Implémenter un rate limiting pour éviter les abus
- 🔐 Logger les exports pour audit

## 📈 Performance

### Optimisations
- ⚡ Génération HTML en mémoire (pas de fichiers temporaires)
- ⚡ Cache possible avec Redis pour les formulaires fréquemment exportés
- ⚡ Génération asynchrone pour les gros formulaires

### Limites recommandées
- 📊 Taille maximale : ~1000 champs par formulaire
- 📊 Temps de génération PDF : ~1-3 secondes
- 📊 Rate limit suggéré : 10 exports/minute/utilisateur

## 🐛 Dépannage

### Erreur : "Échec de la génération du PDF"

**Cause :** WeasyPrint ne peut pas convertir le HTML

**Solutions :**
1. Vérifier que WeasyPrint est installé : `pip list | grep weasyprint`
2. Vérifier les dépendances système (cairo, pango)
3. Tester avec un HTML simple
4. Consulter les logs backend

### Erreur 404 : "Formulaire non trouvé"

**Cause :** L'ID du formulaire n'existe pas

**Solution :** Vérifier l'ID avec `GET /api/v1/formulaires`

### PDF vide ou mal formaté

**Cause :** HTML mal formé ou styles CSS incompatibles

**Solutions :**
1. Tester le HTML dans un navigateur d'abord
2. Vérifier la structure JSON du formulaire
3. Simplifier les styles CSS

## 📚 Ressources

- [WeasyPrint Documentation](https://weasyprint.readthedocs.io/)
- [HTML5 Form Elements](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form)
- [CSS for Print](https://www.smashingmagazine.com/2015/01/designing-for-print-with-css/)

---

**Développé avec ❤️ pour FormBuilder**
