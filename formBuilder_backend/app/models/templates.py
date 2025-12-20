"""
Modèles pour les templates de formulaires prédéfinis
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Text
from sqlalchemy.sql import func
from app.db.base import Base


class FormTemplate(Base):
    """Templates de formulaires prédéfinis"""
    __tablename__ = "form_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identification
    nom = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # contact, event, hr, survey, etc.
    
    # Template data
    structure_json = Column(JSON, nullable=False)
    preview_image_url = Column(String(500), nullable=True)
    
    # Métadonnées
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    # Tags pour recherche
    tags = Column(JSON, nullable=True)  # ["contact", "simple", "professional"]
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class FormTheme(Base):
    """Thèmes visuels personnalisables"""
    __tablename__ = "form_themes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identification
    nom = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration des couleurs
    primary_color = Column(String(7), default="#3b82f6")
    secondary_color = Column(String(7), default="#6366f1")
    accent_color = Column(String(7), default="#8b5cf6")
    background_color = Column(String(7), default="#ffffff")
    text_color = Column(String(7), default="#1f2937")
    
    # Polices
    font_family = Column(String(255), default="Inter, system-ui, sans-serif")
    font_size_base = Column(String(10), default="16px")
    
    # Styles
    border_radius = Column(String(10), default="8px")
    spacing = Column(String(10), default="16px")
    
    # CSS personnalisé
    custom_css = Column(Text, nullable=True)
    
    # Métadonnées
    is_public = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
