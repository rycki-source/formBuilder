"""Schémas Pydantic pour les logs d'erreurs"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.error_log import ErrorSeverity, ErrorType


# Schémas de création
class ErrorLogCreate(BaseModel):
    type_erreur: ErrorType
    severite: ErrorSeverity = ErrorSeverity.MEDIUM
    message: str
    stack_trace: Optional[str] = None
    endpoint: Optional[str] = None
    methode_http: Optional[str] = None
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata_json: Optional[str] = None
    request_data: Optional[str] = None


# Schémas de mise à jour
class ErrorLogUpdate(BaseModel):
    resolu: Optional[bool] = None
    notes: Optional[str] = None


# Schémas de réponse
class ErrorLogResponse(BaseModel):
    id: int
    type_erreur: ErrorType
    severite: ErrorSeverity
    message: str
    stack_trace: Optional[str]
    endpoint: Optional[str]
    methode_http: Optional[str]
    user_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata_json: Optional[str]
    request_data: Optional[str]
    resolu: bool
    notes: Optional[str]
    date_erreur: datetime
    date_resolution: Optional[datetime]

    class Config:
        from_attributes = True


# Schéma simplifié (sans stack trace)
class ErrorLogListResponse(BaseModel):
    id: int
    type_erreur: ErrorType
    severite: ErrorSeverity
    message: str
    endpoint: Optional[str]
    user_id: Optional[int]
    resolu: bool
    date_erreur: datetime

    class Config:
        from_attributes = True


# Schéma pour les statistiques
class ErrorStats(BaseModel):
    total: int
    non_resolus: int
    par_type: dict
    par_severite: dict
    derniere_24h: int
