"""Endpoints API pour la gestion des rôles et permissions"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.role import (
    PermissionCreate, PermissionResponse,
    RoleCreate, RoleUpdate, RoleResponse, RoleListResponse,
    UserRoleAssignment, UserWithRoles
)
from app.services.role_service import RolePermissionService

router = APIRouter(prefix="/admin/roles", tags=["Admin - Rôles & Permissions"])


# ==================== PERMISSIONS ====================

@router.post("/permissions", response_model=PermissionResponse, status_code=201)
async def create_permission(
    permission_data: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une nouvelle permission"""
    # TODO: Vérifier permission admin
    service = RolePermissionService(db)
    permission = await service.create_permission(permission_data)
    return permission


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    categorie: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister toutes les permissions"""
    service = RolePermissionService(db)
    permissions = await service.list_permissions(categorie=categorie)
    return permissions


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer une permission par ID"""
    service = RolePermissionService(db)
    permission = await service.get_permission(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission non trouvée")
    return permission


@router.get("/permissions/by-code/{code}", response_model=PermissionResponse)
async def get_permission_by_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer une permission par code"""
    service = RolePermissionService(db)
    permission = await service.get_permission_by_code(code)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission non trouvée")
    return permission


# ==================== RÔLES ====================

@router.post("/", response_model=RoleResponse, status_code=201)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau rôle"""
    # TODO: Vérifier permission admin
    service = RolePermissionService(db)
    role = await service.create_role(role_data)
    return role


@router.get("/", response_model=List[RoleListResponse])
async def list_roles(
    actif: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister tous les rôles"""
    service = RolePermissionService(db)
    roles = await service.list_roles(actif=actif)
    return roles


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un rôle par ID avec ses permissions"""
    service = RolePermissionService(db)
    role = await service.get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rôle non trouvé")
    return role


@router.get("/by-code/{code}", response_model=RoleResponse)
async def get_role_by_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un rôle par code"""
    service = RolePermissionService(db)
    role = await service.get_role_by_code(code)
    if not role:
        raise HTTPException(status_code=404, detail="Rôle non trouvé")
    return role


@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un rôle"""
    # TODO: Vérifier permission admin
    service = RolePermissionService(db)
    role = await service.update_role(role_id, role_data)
    if not role:
        raise HTTPException(status_code=404, detail="Rôle non trouvé")
    return role


@router.delete("/{role_id}", status_code=204)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un rôle (si non système)"""
    # TODO: Vérifier permission admin
    service = RolePermissionService(db)
    success = await service.delete_role(role_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer le rôle (rôle système ou introuvable)"
        )


# ==================== AFFECTATION UTILISATEURS ====================

@router.post("/users/{user_id}/assign", response_model=UserWithRoles)
async def assign_roles_to_user(
    user_id: int,
    assignment: UserRoleAssignment,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Affecter des rôles à un utilisateur"""
    # TODO: Vérifier permission admin
    service = RolePermissionService(db)
    user = await service.assign_roles_to_user(user_id, assignment.role_ids)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user


@router.get("/users/{user_id}/roles", response_model=UserWithRoles)
async def get_user_roles(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir les rôles d'un utilisateur"""
    service = RolePermissionService(db)
    user = await service.get_user_roles(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user


@router.get("/users/{user_id}/permissions", response_model=List[PermissionResponse])
async def get_user_permissions(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir toutes les permissions d'un utilisateur"""
    service = RolePermissionService(db)
    permissions = await service.get_user_permissions(user_id)
    return permissions


@router.get("/users/{user_id}/has-permission/{permission_code}", response_model=dict)
async def check_user_permission(
    user_id: int,
    permission_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Vérifier si un utilisateur a une permission"""
    service = RolePermissionService(db)
    has_permission = await service.user_has_permission(user_id, permission_code)
    return {"user_id": user_id, "permission_code": permission_code, "has_permission": has_permission}
