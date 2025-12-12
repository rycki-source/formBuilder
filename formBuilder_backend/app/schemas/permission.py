"""Schémas Pydantic pour les permissions"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PermissionBase(BaseModel):
    code: str = Field(..., max_length=100, description="Code unique de la permission")
    nom: str = Field(..., max_length=255, description="Nom lisible")
    description: Optional[str] = Field(None, description="Description détaillée")
    categorie: Optional[str] = Field(None, max_length=50, description="Catégorie")
    actif: bool = Field(True, description="Permission active")

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    categorie: Optional[str] = Field(None, max_length=50)
    actif: Optional[bool] = None

class PermissionResponse(PermissionBase):
    id: int
    date_creation: datetime
    
    class Config:
        from_attributes = True

class PermissionList(BaseModel):
    items: list[PermissionResponse]
    total: int
    page: int
    size: int
