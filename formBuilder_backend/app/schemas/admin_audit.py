"""Schémas Pydantic pour l'audit log"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AdminAuditCreate(BaseModel):
    user_id: int
    username: str
    action: str = Field(..., max_length=100)
    resource_type: str = Field(..., max_length=50)
    resource_id: Optional[int] = None
    description: str
    changes_json: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


class AdminAuditResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: str
    action: str
    resource_type: str
    resource_id: Optional[int]
    description: str
    changes_json: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    endpoint: Optional[str]
    success: bool
    error_message: Optional[str]
    date_action: datetime

    class Config:
        from_attributes = True


class AdminAuditStats(BaseModel):
    total_actions: int
    actions_reussies: int
    actions_echouees: int
    par_type: dict
    derniere_24h: int
