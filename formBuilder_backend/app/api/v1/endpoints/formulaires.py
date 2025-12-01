from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from app.schemas.formulaire import FormulaireCreate, FormulaireResponse, FormulaireUpdate
from app.services.formulaire_service import FormulaireService
from app.api.dependencies import get_current_user
from app.utils.pdf_generator import PDFGenerator
from typing import List

router = APIRouter(prefix="/formulaires", tags=["formulaires"])

@router.post("/", response_model=FormulaireResponse, status_code=201)
async def create_formulaire(
    form_data: FormulaireCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Créer un nouveau formulaire"""
    service = FormulaireService(db)
    formulaire = await service.create_formulaire(form_data, getattr(current_user, "id"))
    return formulaire

@router.get("/user", response_model=List[FormulaireResponse])
async def list_user_formulaires(
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        """Lister les formulaires de l'utilisateur connecté"""
        service = FormulaireService(db)
        user_id: int = current_user.id  # type: ignore
        formulaires = await service.list_user_formulaires(user_id, skip, limit)
        return formulaires

@router.get("/", response_model=List[FormulaireResponse])
async def list_formulaires(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister tous les formulaires"""
    service = FormulaireService(db)
    formulaires = await service.list_formulaires(skip, limit)
    return formulaires

@router.get("/{formulaire_id}", response_model=FormulaireResponse)
async def get_formulaire(
    formulaire_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Récupérer un formulaire par ID"""
    service = FormulaireService(db)
    formulaire = await service.get_formulaire(formulaire_id)
    
    if not formulaire:
        raise HTTPException(status_code=404, detail="Formulaire non trouvé")
    
    return formulaire

@router.put("/{formulaire_id}", response_model=FormulaireResponse)
async def update_formulaire(
    formulaire_id: int,
    form_data: FormulaireUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mettre à jour un formulaire"""
    service = FormulaireService(db)
    formulaire = await service.update_formulaire(formulaire_id, form_data)
    
    if not formulaire:
        raise HTTPException(status_code=404, detail="Formulaire non trouvé")
    
    return formulaire

@router.post("/{formulaire_id}/publish")
async def publish_formulaire(
    formulaire_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Publier un formulaire"""
    service = FormulaireService(db)
    formulaire = await service.publish_formulaire(formulaire_id)
    
    if not formulaire:
        raise HTTPException(status_code=404, detail="Formulaire non trouvé")
    
    return {"message": "Formulaire publié", "formulaire": formulaire}

@router.delete("/{formulaire_id}", status_code=204)
async def delete_formulaire(
    formulaire_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Supprimer un formulaire (soft delete)"""
    service = FormulaireService(db)
    success = await service.delete_formulaire(formulaire_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Formulaire non trouvé")
    
    return None


def generate_form_html(formulaire: dict, include_wrapper: bool = True, for_pdf: bool = False) -> str:
    """Générer le HTML d'un formulaire pour intégration"""
    structure = formulaire.get('structure_json', {})
    champs = structure.get('champs', [])
    etapes = structure.get('etapes', [])
    type_structurel = formulaire.get('type_structurel', 'simple')
    formulaire_id = formulaire.get('id')
    
    # Style CSS intégré
    css = """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f9fafb;
            padding: 40px 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            padding: 40px;
        }
        .header {
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 24px;
            margin-bottom: 32px;
        }
        h1 {
            font-size: 32px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 8px;
        }
        .description {
            font-size: 16px;
            color: #6b7280;
            margin-top: 8px;
        }
        .badge {
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            margin-top: 12px;
        }
        .form-section {
            margin-bottom: 32px;
        }
        .step-header {
            background: #f3f4f6;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 24px;
        }
        .step-title {
            font-size: 20px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 4px;
        }
        .step-description {
            font-size: 14px;
            color: #6b7280;
        }
        .field-group {
            margin-bottom: 24px;
        }
        label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: #374151;
            margin-bottom: 8px;
        }
        .required {
            color: #ef4444;
        }
        input[type="text"],
        input[type="email"],
        input[type="number"],
        input[type="date"],
        input[type="file"],
        select,
        textarea {
            width: 100%;
            padding: 10px 14px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
            color: #111827;
            background-color: white;
        }
        input:focus,
        select:focus,
        textarea:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        .checkbox-wrapper,
        .radio-wrapper {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        input[type="checkbox"],
        input[type="radio"] {
            width: 16px;
            height: 16px;
            margin-right: 8px;
        }
        .checkbox-wrapper label,
        .radio-wrapper label {
            margin-bottom: 0;
            font-weight: normal;
        }
        .button {
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
        }
        .button-primary {
            background-color: #3b82f6;
            color: white;
        }
        .button-secondary {
            background-color: #6b7280;
            color: white;
        }
        .button-danger {
            background-color: #ef4444;
            color: white;
        }
        .footer {
            margin-top: 40px;
            padding-top: 24px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            color: #9ca3af;
            font-size: 12px;
        }
    </style>
    """
    
    # JavaScript pour la soumission
    javascript = f"""
    <script>
        // Configuration de l'API
        const API_BASE_URL = 'http://localhost:8000/api/v1';
        const FORMULAIRE_ID = {formulaire_id};
        
        // Fonction de soumission
        async function submitForm(event) {{
            event.preventDefault();
            
            const form = event.target;
            const formData = new FormData(form);
            const data = {{}};
            
            // Convertir FormData en objet
            for (let [key, value] of formData.entries()) {{
                if (data[key]) {{
                    // Si la clé existe déjà, créer un tableau
                    if (Array.isArray(data[key])) {{
                        data[key].push(value);
                    }} else {{
                        data[key] = [data[key], value];
                    }}
                }} else {{
                    data[key] = value;
                }}
            }}
            
            // Gérer les checkboxes non cochées
            const checkboxes = form.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(cb => {{
                if (!cb.checked && !data[cb.name]) {{
                    data[cb.name] = false;
                }}
            }});
            
            try {{
                const response = await fetch(`${{API_BASE_URL}}/soumissions`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        formulaire_id: FORMULAIRE_ID,
                        donnees: data
                    }})
                }});
                
                if (response.ok) {{
                    const result = await response.json();
                    alert('✅ Formulaire soumis avec succès!');
                    form.reset();
                    console.log('Réponse:', result);
                }} else {{
                    const error = await response.json();
                    alert('❌ Erreur: ' + (error.detail || 'Erreur lors de la soumission'));
                }}
            }} catch (error) {{
                console.error('Erreur:', error);
                alert('❌ Erreur de connexion au serveur');
            }}
        }}
        
        // Validation en temps réel
        document.addEventListener('DOMContentLoaded', function() {{
            const form = document.getElementById('formbuilder-form');
            if (form) {{
                form.addEventListener('submit', submitForm);
                
                // Validation des champs obligatoires
                const requiredFields = form.querySelectorAll('[required]');
                requiredFields.forEach(field => {{
                    field.addEventListener('invalid', function() {{
                        this.setCustomValidity('Ce champ est obligatoire');
                    }});
                    field.addEventListener('input', function() {{
                        this.setCustomValidity('');
                    }});
                }});
            }}
        }});
    </script>
    """
    
    # Construction du HTML
    if include_wrapper:
        html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{formulaire.get('nom', 'Formulaire')}</title>
        {css}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{formulaire.get('nom', 'Formulaire')}</h1>
                <span class="badge">{type_structurel}</span>
                {f'<p class="description">{formulaire.get("description")}</p>' if formulaire.get('description') else ''}
            </div>
            
            <form id="formbuilder-form">
    """
    else:
        # Version sans wrapper pour intégration
        html = f"""
        <!-- FormBuilder - {formulaire.get('nom')} -->
        {css}
        <div class="formbuilder-container">
            <div class="formbuilder-header">
                <h2>{formulaire.get('nom', 'Formulaire')}</h2>
                <span class="badge">{type_structurel}</span>
                {f'<p class="description">{formulaire.get("description")}</p>' if formulaire.get('description') else ''}
            </div>
            
            <form id="formbuilder-form-{formulaire_id}">
    """
    
    # Formulaire multi-étapes
    if type_structurel in ['multi-etapes', 'wizard'] and etapes:
        for idx, etape in enumerate(etapes, 1):
            html += f"""
                <div class="form-section">
                    <div class="step-header">
                        <div class="step-title">Étape {idx}: {etape.get('titre', f'Étape {idx}')}</div>
                        {f'<div class="step-description">{etape.get("description")}</div>' if etape.get('description') else ''}
                    </div>
            """
            
            # Champs de l'étape
            champs_etape = etape.get('champs', [])
            for champ in champs_etape:
                html += generate_field_html(champ)
            
            html += "</div>"
    
    # Formulaire simple
    else:
        html += '<div class="form-section">'
        for champ in champs:
            html += generate_field_html(champ)
        html += '</div>'
    
    # Boutons de soumission
    html += """
                <div class="field-group">
                    <button type="submit" class="button button-primary">Soumettre</button>
                    <button type="reset" class="button button-secondary" style="margin-left: 10px;">Réinitialiser</button>
                </div>
            </form>
    """
    
    if include_wrapper:
        html += """
            <div class="footer">
                Généré par FormBuilder
            </div>
        </div>
        """
        # N'inclure le JavaScript que si ce n'est pas pour PDF
        if not for_pdf:
            html += javascript
        html += """
    </body>
    </html>
    """
    else:
        html += """
        </div>
        <!-- Fin FormBuilder -->
        """
        # N'inclure le JavaScript que si ce n'est pas pour PDF
        if not for_pdf:
            html += javascript
    
    return html


def generate_field_html(champ: dict) -> str:
    """Générer le HTML d'un champ"""
    type_champ = champ.get('type_champ', 'text')
    label = champ.get('label', 'Champ')
    obligatoire = champ.get('obligatoire', False)
    placeholder = champ.get('placeholder', '')
    options = champ.get('options', [])
    
    # Créer un nom de champ sécurisé (utilisé comme name attribute)
    field_name = label.lower().replace(' ', '_').replace("'", '').replace('"', '')
    
    required_attr = 'required' if obligatoire else ''
    required_mark = '<span class="required">*</span>' if obligatoire else ''
    
    html = '<div class="field-group">'
    
    if type_champ == 'text':
        html += f"""
            <label for="{field_name}">{label} {required_mark}</label>
            <input type="text" id="{field_name}" name="{field_name}" placeholder="{placeholder}" {required_attr} />
        """
    
    elif type_champ == 'email':
        html += f"""
            <label for="{field_name}">{label} {required_mark}</label>
            <input type="email" id="{field_name}" name="{field_name}" placeholder="{placeholder}" {required_attr} />
        """
    
    elif type_champ == 'number':
        html += f"""
            <label for="{field_name}">{label} {required_mark}</label>
            <input type="number" id="{field_name}" name="{field_name}" placeholder="{placeholder}" {required_attr} />
        """
    
    elif type_champ == 'date':
        html += f"""
            <label for="{field_name}">{label} {required_mark}</label>
            <input type="date" id="{field_name}" name="{field_name}" {required_attr} />
        """
    
    elif type_champ == 'select':
        html += f"""
            <label for="{field_name}">{label} {required_mark}</label>
            <select id="{field_name}" name="{field_name}" {required_attr}>
                <option value="">Sélectionnez une option</option>
        """
        for option in options:
            html += f'<option value="{option}">{option}</option>'
        html += '</select>'
    
    elif type_champ == 'textarea':
        html += f"""
            <label for="{field_name}">{label} {required_mark}</label>
            <textarea id="{field_name}" name="{field_name}" placeholder="{placeholder}" {required_attr}></textarea>
        """
    
    elif type_champ == 'checkbox':
        html += f"""
            <div class="checkbox-wrapper">
                <input type="checkbox" id="{field_name}" name="{field_name}" value="true" {required_attr} />
                <label for="{field_name}">{label} {required_mark}</label>
            </div>
        """
    
    elif type_champ == 'radio':
        html += f'<label>{label} {required_mark}</label>'
        for idx, option in enumerate(options):
            option_id = f"{field_name}_{idx}"
            html += f"""
            <div class="radio-wrapper">
                <input type="radio" id="{option_id}" name="{field_name}" value="{option}" {required_attr} />
                <label for="{option_id}">{option}</label>
            </div>
            """
    
    elif type_champ == 'file':
        html += f"""
            <label for="{field_name}">{label} {required_mark}</label>
            <input type="file" id="{field_name}" name="{field_name}" {required_attr} />
        """
    
    elif type_champ == 'button':
        button_type = champ.get('buttonType', 'button')
        button_style = champ.get('buttonStyle', 'primary')
        html += f"""
            <button type="{button_type}" class="button button-{button_style}">{label}</button>
        """
    
    html += '</div>'
    return html


@router.get("/{formulaire_id}/html", response_class=HTMLResponse)
async def get_formulaire_html(
    formulaire_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Récupérer le formulaire en HTML"""
    service = FormulaireService(db)
    formulaire = await service.get_formulaire(formulaire_id)
    
    if not formulaire:
        raise HTTPException(status_code=404, detail="Formulaire non trouvé")
    
    # Convertir le formulaire en dict
    formulaire_dict = {
        'id': formulaire.id,
        'nom': formulaire.nom,
        'description': formulaire.description,
        'type_structurel': formulaire.type_structurel,
        'type_fonctionnel': formulaire.type_fonctionnel,
        'structure_json': formulaire.structure_json
    }
    
    html_content = generate_form_html(formulaire_dict)
    return HTMLResponse(content=html_content)


@router.get("/{formulaire_id}/embed", response_class=HTMLResponse)
async def get_formulaire_embed(
    formulaire_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Récupérer le code HTML embarquable (pour intégration dans une autre application)"""
    service = FormulaireService(db)
    formulaire = await service.get_formulaire(formulaire_id)
    
    if not formulaire:
        raise HTTPException(status_code=404, detail="Formulaire non trouvé")
    
    # Convertir le formulaire en dict
    formulaire_dict = {
        'id': formulaire.id,
        'nom': formulaire.nom,
        'description': formulaire.description,
        'type_structurel': formulaire.type_structurel,
        'type_fonctionnel': formulaire.type_fonctionnel,
        'structure_json': formulaire.structure_json
    }
    
    # Générer le HTML sans wrapper (pour intégration)
    html_content = generate_form_html(formulaire_dict, include_wrapper=False)
    return HTMLResponse(content=html_content)


@router.get("/{formulaire_id}/pdf")
async def get_formulaire_pdf(
    formulaire_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Récupérer le formulaire en PDF (code HTML source)"""
    service = FormulaireService(db)
    formulaire = await service.get_formulaire(formulaire_id)
    
    if not formulaire:
        raise HTTPException(status_code=404, detail="Formulaire non trouvé")
    
    # Convertir le formulaire en dict
    formulaire_dict = {
        'id': formulaire.id,
        'nom': formulaire.nom,
        'description': formulaire.description,
        'type_structurel': formulaire.type_structurel,
        'type_fonctionnel': formulaire.type_fonctionnel,
        'structure_json': formulaire.structure_json
    }
    
    # Générer le code HTML du formulaire (pour intégration)
    form_html_code = generate_form_html(formulaire_dict, include_wrapper=False, for_pdf=False)
    
    # Créer un document HTML qui affiche le code HTML source
    html_wrapper = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Code HTML - {formulaire.nom}</title>
        <style>
            body {{
                font-family: 'Courier New', Courier, monospace;
                margin: 40px;
                background-color: #f5f5f5;
            }}
            .header {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid #3b82f6;
            }}
            h1 {{
                margin: 0;
                font-size: 24px;
                color: #1f2937;
            }}
            .info {{
                margin-top: 8px;
                font-size: 14px;
                color: #6b7280;
            }}
            .code-container {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
            }}
            pre {{
                margin: 0;
                white-space: pre-wrap;
                word-wrap: break-word;
                font-size: 10px;
                line-height: 1.5;
                color: #111827;
            }}
            .footer {{
                margin-top: 20px;
                text-align: center;
                font-size: 12px;
                color: #9ca3af;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Code HTML du Formulaire</h1>
            <div class="info">
                Formulaire: {formulaire.nom}<br>
                ID: {formulaire.id}<br>
                Type: {formulaire.type_structurel}
            </div>
        </div>
        <div class="code-container">
            <pre>{form_html_code.replace('<', '&lt;').replace('>', '&gt;')}</pre>
        </div>
        <div class="footer">
            Généré par FormBuilder - Code prêt à intégrer
        </div>
    </body>
    </html>
    """
    
    # Générer le PDF à partir du wrapper HTML
    try:
        pdf_bytes = PDFGenerator.generate_from_html(html_wrapper)
        
        # Nom de fichier sécurisé
        filename = f"code_html_formulaire_{formulaire_id}_{formulaire.nom.replace(' ', '_')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du PDF: {str(e)}"
        )