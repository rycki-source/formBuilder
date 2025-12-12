"""Schémas pour les soumissions"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime


class SoumissionCreate(BaseModel):
    formulaire_id: int
    donnees: Dict[str, Any]


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
