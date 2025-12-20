"""Schémas pour les soumissions"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Any, Dict, Literal
from datetime import datetime

# Statuts autorisés pour les soumissions
StatutSoumission = Literal["SOUMIS", "EN_ATTENTE", "VALIDEE", "REJETEE"]


class SoumissionCreate(BaseModel):
    formulaire_id: int = Field(..., gt=0, description="ID du formulaire")
    donnees: Dict[str, Any] = Field(..., description="Données saisies dans le formulaire")
    reponses: Optional[Dict[str, Any]] = None  # Pour compatibilité
    statut: Optional[StatutSoumission] = "SOUMIS"
    
    @validator('formulaire_id')
    def validate_formulaire_id(cls, v):
        if not isinstance(v, int) or v <= 0:
            raise ValueError('formulaire_id doit être un entier positif')
        return v


class SoumissionUpdate(BaseModel):
    statut: Optional[str] = None
    donnees: Optional[Dict[str, Any]] = None


class SoumissionResponse(BaseModel):
    id: int
    formulaire_id: int
    donnees: Dict[str, Any]
    statut: str
    date_soumission: datetime

    class Config:
        from_attributes = True


class ExportRequest(BaseModel):
    format: str = Field(..., pattern="^(csv|excel|pdf|json)$")
    soumission_ids: Optional[list] = None
