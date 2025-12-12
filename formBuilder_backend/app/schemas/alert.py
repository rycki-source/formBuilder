"""Schémas Pydantic pour les alertes"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.admin_alert import AlertStatus, AlertType


# Schémas de création
class AlertCreate(BaseModel):
    titre: str = Field(..., max_length=255)
    message: str
    status: AlertStatus = AlertStatus.INFO
    type: AlertType = AlertType.SYSTEM
    metadata_json: Optional[str] = None
    source: Optional[str] = None
    user_id: Optional[int] = None
    persistent: bool = True
    date_expiration: Optional[datetime] = None


# Schémas de mise à jour
class AlertUpdate(BaseModel):
    lu: Optional[bool] = None
    archive: Optional[bool] = None
    notes: Optional[str] = None


# Schémas de réponse
class AlertResponse(BaseModel):
    id: int
    titre: str
    message: str
    status: AlertStatus
    type: AlertType
    metadata_json: Optional[str]
    source: Optional[str]
    user_id: Optional[int]
    lu: bool
    persistent: bool
    archive: bool
    date_creation: datetime
    date_lecture: Optional[datetime]
    date_expiration: Optional[datetime]

    class Config:
        from_attributes = True


# Schéma pour les statistiques
class AlertStats(BaseModel):
    total: int
    non_lues: int
    par_statut: dict[str, int]
    par_type: dict[str, int]
