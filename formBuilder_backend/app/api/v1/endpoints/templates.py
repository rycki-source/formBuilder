"""
Endpoints pour les templates de formulaires
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.template_service import TemplateService
from app.api.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel
from typing import Optional, List, Dict

router = APIRouter(prefix="/templates", tags=["templates"])


class CreateTemplateRequest(BaseModel):
    nom: str
    description: str
    category: str
    structure_json: Dict
    tags: Optional[List[str]] = None
    preview_image_url: Optional[str] = None


class CreateThemeRequest(BaseModel):
    nom: str
    primary_color: str = "#3b82f6"
    secondary_color: str = "#6366f1"
    accent_color: str = "#8b5cf6"
    background_color: str = "#ffffff"
    text_color: str = "#1f2937"
    font_family: str = "Inter, system-ui, sans-serif"
    custom_css: Optional[str] = None


@router.get("/")
async def get_all_templates(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Récupérer tous les templates (public)"""
    service = TemplateService(db)
    templates = await service.get_all_templates(category=category, search=search)
    
    return {
        "templates": [
            {
                "id": t.id,
                "nom": t.nom,
                "description": t.description,
                "category": t.category,
                "tags": t.tags,
                "preview_image_url": t.preview_image_url,
                "usage_count": t.usage_count,
                "is_featured": t.is_featured
            }
            for t in templates
        ]
    }


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Récupérer toutes les catégories"""
    service = TemplateService(db)
    categories = await service.get_categories()
    return {"categories": categories}


@router.get("/{template_id}")
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Récupérer un template spécifique"""
    service = TemplateService(db)
    template = await service.get_template(template_id)
    
    return {
        "id": template.id,
        "nom": template.nom,
        "description": template.description,
        "category": template.category,
        "structure_json": template.structure_json,
        "tags": template.tags,
        "preview_image_url": template.preview_image_url,
        "usage_count": template.usage_count
    }


@router.post("/{template_id}/use")
async def create_formulaire_from_template(
    template_id: int,
    custom_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un formulaire à partir d'un template"""
    service = TemplateService(db)
    formulaire = await service.create_formulaire_from_template(
        template_id=template_id,
        user_id=int(current_user.id),  # type: ignore
        custom_name=custom_name
    )
    
    return {
        "formulaire_id": formulaire.id,
        "nom": formulaire.nom,
        "message": "Formulaire créé avec succès à partir du template"
    }


@router.post("/")
async def create_template(
    data: CreateTemplateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau template (admin uniquement)"""
    if getattr(current_user, 'role', None) != "ADMIN":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    service = TemplateService(db)
    template = await service.create_template(
        nom=data.nom,
        description=data.description,
        category=data.category,
        structure_json=data.structure_json,
        tags=data.tags,
        preview_image_url=data.preview_image_url
    )
    
    return {"template_id": template.id, "message": "Template créé avec succès"}


# Endpoints pour les thèmes
@router.get("/themes/")
async def get_all_themes(db: AsyncSession = Depends(get_db)):
    """Récupérer tous les thèmes"""
    service = TemplateService(db)
    themes = await service.get_all_themes()
    
    return {
        "themes": [
            {
                "id": t.id,
                "nom": t.nom,
                "primary_color": t.primary_color,
                "secondary_color": t.secondary_color,
                "accent_color": t.accent_color,
                "background_color": t.background_color,
                "text_color": t.text_color,
                "font_family": t.font_family,
                "is_default": t.is_default
            }
            for t in themes
        ]
    }


@router.post("/themes/")
async def create_theme(
    data: CreateThemeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau thème"""
    service = TemplateService(db)
    theme = await service.create_theme(
        nom=data.nom,
        primary_color=data.primary_color,
        secondary_color=data.secondary_color,
        accent_color=data.accent_color,
        background_color=data.background_color,
        text_color=data.text_color,
        font_family=data.font_family,
        custom_css=data.custom_css
    )
    
    return {"theme_id": theme.id, "message": "Thème créé avec succès"}


@router.put("/formulaire/{formulaire_id}/theme/{theme_id}")
async def apply_theme(
    formulaire_id: int,
    theme_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Appliquer un thème à un formulaire"""
    service = TemplateService(db)
    await service.apply_theme_to_form(formulaire_id, theme_id)
    
    return {"message": "Thème appliqué avec succès"}
