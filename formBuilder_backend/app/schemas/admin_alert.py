"""Schémas Pydantic pour les alertes administratives"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.admin_alert import AlertStatus, AlertType

class AlertBase(BaseModel):
    titre: str = Field(..., max_length=255, description="Titre de l'alerte")
    message: str = Field(..., description="Message détaillé")
    statut: AlertStatus = Field(AlertStatus.INFO, description="Statut de l'alerte")
    type_alert: AlertType = Field(AlertType.SYSTEM, description="Type d'alerte")
    persistant: bool = Field(True, description="Persistante ou temporaire")

class AlertCreate(AlertBase):
    utilisateur_id: Optional[int] = None
    formulaire_id: Optional[int] = None
    metadata_json: Optional[str] = None
    date_expiration: Optional[datetime] = None

class AlertUpdate(BaseModel):
    lu: Optional[bool] = None
    date_lecture: Optional[datetime] = None

class AlertResponse(AlertBase):
    id: int
    lu: bool
    utilisateur_id: Optional[int]
    formulaire_id: Optional[int]
    metadata_json: Optional[str]
    date_creation: datetime
    date_lecture: Optional[datetime]
    date_expiration: Optional[datetime]
    
    class Config:
        from_attributes = True

class AlertList(BaseModel):
    items: list[AlertResponse]
    total: int
    non_lues: int
    page: int
    size: int

class AlertStats(BaseModel):
    total: int
    non_lues: int
    par_statut: dict[str, int]
    par_type: dict[str, int]
