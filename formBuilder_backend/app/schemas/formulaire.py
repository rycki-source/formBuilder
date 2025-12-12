"""Schémas pour les formulaires"""

from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
from datetime import datetime


class ChampBase(BaseModel):
    nom: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    type: str
    obligatoire: bool = False
    ordre: int


class ChampCreate(ChampBase):
    pass


class ChampResponse(ChampBase):
    id: int
    formulaire_id: int

    class Config:
        from_attributes = True


class RegleValidationBase(BaseModel):
    type: str
    expression: Optional[str] = None
    message_erreur: str


class RegleValidationResponse(RegleValidationBase):
    id: int
    champ_id: int

    class Config:
        from_attributes = True


class FormulaireBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type_structurel: str = Field(default='simple')
    type_fonctionnel: str = Field(default='personnalise')
    structure_json: Dict[str, Any]


class FormulaireCreate(FormulaireBase):
    pass


class FormulaireUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    type_structurel: Optional[str] = None
    type_fonctionnel: Optional[str] = None
    structure_json: Optional[Dict[str, Any]] = None
    publie: Optional[bool] = None
    webhook_url: Optional[str] = None
    webhook_enabled: Optional[bool] = None
    webhook_secret: Optional[str] = None
    webhook_retry_count: Optional[int] = Field(None, ge=1, le=10)


class FormulaireResponse(FormulaireBase):
    id: int
    version: str
    actif: bool
    publie: bool
    type_structurel: str
    type_fonctionnel: str
    date_creation: datetime
    date_modification: datetime
    webhook_url: Optional[str] = None
    webhook_enabled: Optional[bool] = False
    webhook_retry_count: Optional[int] = 3

    class Config:
        from_attributes = True
