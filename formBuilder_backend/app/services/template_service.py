"""
Service pour les templates de formulaires prédéfinis
"""
from typing import List, Dict, Optional
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.templates import FormTemplate, FormTheme
from app.models.formulaire import Formulaire


class TemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_templates(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[FormTemplate]:
        """Récupérer tous les templates actifs"""
        query = select(FormTemplate).where(FormTemplate.is_active == True)
        
        if category:
            query = query.where(FormTemplate.category == category)
        
        if search:
            query = query.where(
                or_(
                    FormTemplate.nom.ilike(f"%{search}%"),
                    FormTemplate.description.ilike(f"%{search}%")
                )
            )
        
        query = query.order_by(FormTemplate.is_featured.desc(), FormTemplate.usage_count.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_template(self, template_id: int) -> FormTemplate:
        """Récupérer un template spécifique"""
        result = await self.db.execute(
            select(FormTemplate).where(FormTemplate.id == template_id)
        )
        return result.scalar_one()
    
    async def create_formulaire_from_template(
        self,
        template_id: int,
        user_id: int,
        custom_name: Optional[str] = None
    ) -> Formulaire:
        """Créer un formulaire à partir d'un template"""
        # Récupérer le template
        template = await self.get_template(template_id)
        
        # Incrémenter le compteur d'utilisation
        template.usage_count += 1  # type: ignore
        
        # Créer le formulaire
        formulaire = Formulaire(
            nom=custom_name or f"{template.nom} - Copie",
            description=template.description,
            structure_json=template.structure_json,
            type_structurel="simple",  # Valeur par défaut
            type_fonctionnel="personnalise",
            developpeur_id=user_id,
            actif=True,
            publie=False
        )
        
        self.db.add(formulaire)
        await self.db.commit()
        await self.db.refresh(formulaire)
        
        return formulaire
    
    async def create_template(
        self,
        nom: str,
        description: str,
        category: str,
        structure_json: Dict,
        tags: Optional[List[str]] = None,
        preview_image_url: Optional[str] = None
    ) -> FormTemplate:
        """Créer un nouveau template"""
        template = FormTemplate(
            nom=nom,
            description=description,
            category=category,
            structure_json=structure_json,
            tags=tags,
            preview_image_url=preview_image_url,
            is_active=True
        )
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        
        return template
    
    async def get_categories(self) -> List[Dict]:
        """Récupérer toutes les catégories avec leur nombre de templates"""
        result = await self.db.execute(
            select(
                FormTemplate.category,
                func.count(FormTemplate.id).label('count')
            )
            .where(FormTemplate.is_active == True)
            .group_by(FormTemplate.category)
            .order_by(func.count(FormTemplate.id).desc())
        )
        
        return [
            {"category": row.category, "count": row.count}
            for row in result
        ]
    
    # Gestion des thèmes
    async def get_all_themes(self) -> List[FormTheme]:
        """Récupérer tous les thèmes"""
        result = await self.db.execute(
            select(FormTheme).order_by(FormTheme.is_default.desc(), FormTheme.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_theme(self, theme_id: int) -> FormTheme:
        """Récupérer un thème spécifique"""
        result = await self.db.execute(
            select(FormTheme).where(FormTheme.id == theme_id)
        )
        return result.scalar_one()
    
    async def create_theme(
        self,
        nom: str,
        primary_color: str = "#3b82f6",
        secondary_color: str = "#6366f1",
        accent_color: str = "#8b5cf6",
        background_color: str = "#ffffff",
        text_color: str = "#1f2937",
        font_family: str = "Inter, system-ui, sans-serif",
        custom_css: Optional[str] = None
    ) -> FormTheme:
        """Créer un nouveau thème"""
        theme = FormTheme(
            nom=nom,
            primary_color=primary_color,
            secondary_color=secondary_color,
            accent_color=accent_color,
            background_color=background_color,
            text_color=text_color,
            font_family=font_family,
            custom_css=custom_css
        )
        
        self.db.add(theme)
        await self.db.commit()
        await self.db.refresh(theme)
        
        return theme
    
    async def apply_theme_to_form(self, formulaire_id: int, theme_id: int):
        """Appliquer un thème à un formulaire"""
        result = await self.db.execute(
            select(Formulaire).where(Formulaire.id == formulaire_id)
        )
        formulaire = result.scalar_one()
        
        formulaire.theme_id = theme_id  # type: ignore
        await self.db.commit()


async def seed_default_templates(db: AsyncSession):
    """Créer les templates par défaut"""
    service = TemplateService(db)
    
    templates = [
        {
            "nom": "Formulaire de Contact",
            "description": "Un formulaire simple pour contacter votre équipe",
            "category": "contact",
            "tags": ["contact", "simple", "business"],
            "structure_json": {
                "champs": [
                    {"nom": "nom", "label": "Nom", "type_champ": "text", "obligatoire": True},
                    {"nom": "email", "label": "Email", "type_champ": "email", "obligatoire": True},
                    {"nom": "sujet", "label": "Sujet", "type_champ": "text", "obligatoire": True},
                    {"nom": "message", "label": "Message", "type_champ": "textarea", "obligatoire": True}
                ]
            }
        },
        {
            "nom": "Inscription Événement",
            "description": "Formulaire d'inscription pour événements et conférences",
            "category": "event",
            "tags": ["event", "registration", "conference"],
            "structure_json": {
                "champs": [
                    {"nom": "nom_complet", "label": "Nom complet", "type_champ": "text", "obligatoire": True},
                    {"nom": "email", "label": "Email", "type_champ": "email", "obligatoire": True},
                    {"nom": "telephone", "label": "Téléphone", "type_champ": "tel", "obligatoire": False},
                    {"nom": "entreprise", "label": "Entreprise", "type_champ": "text", "obligatoire": False},
                    {"nom": "regime_alimentaire", "label": "Régime alimentaire", "type_champ": "select", "obligatoire": False}
                ]
            }
        },
        {
            "nom": "Sondage de Satisfaction",
            "description": "Recueillez l'avis de vos clients",
            "category": "survey",
            "tags": ["survey", "feedback", "satisfaction"],
            "structure_json": {
                "champs": [
                    {"nom": "satisfaction", "label": "Niveau de satisfaction", "type_champ": "radio", "obligatoire": True},
                    {"nom": "recommandation", "label": "Recommanderiez-vous nos services?", "type_champ": "radio", "obligatoire": True},
                    {"nom": "commentaires", "label": "Commentaires", "type_champ": "textarea", "obligatoire": False}
                ]
            }
        }
    ]
    
    for template_data in templates:
        try:
            await service.create_template(**template_data)
        except Exception as e:
            print(f"Template déjà existant ou erreur: {e}")
