"""Schémas Pydantic pour les rôles et permissions"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ===== PERMISSIONS =====

class PermissionBase(BaseModel):
    code: str = Field(..., max_length=100)
    nom: str = Field(..., max_length=255)
    description: Optional[str] = None
    categorie: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int
    date_creation: datetime

    class Config:
        from_attributes = True


# ===== ROLES =====

class RoleBase(BaseModel):
    code: str = Field(..., max_length=50)
    nom: str = Field(..., max_length=255)
    description: Optional[str] = None
    actif: bool = True


class RoleCreate(RoleBase):
    permission_ids: List[int] = []


class RoleUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    actif: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    id: int
    is_system: bool
    permissions: List[PermissionResponse]
    date_creation: datetime
    date_modification: Optional[datetime]

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    id: int
    code: str
    nom: str
    actif: bool
    nombre_permissions: int

    class Config:
        from_attributes = True


# ===== USER ROLES =====

class UserRoleAssignment(BaseModel):
    user_id: int
    role_ids: List[int]


class UserWithRoles(BaseModel):
    id: int
    username: str
    email: str
    roles: List[RoleResponse]

    class Config:
        from_attributes = True
