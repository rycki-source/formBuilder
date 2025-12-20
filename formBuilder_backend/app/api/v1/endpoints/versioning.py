"""
Endpoints pour le versioning et l'audit log
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.versioning_service import VersioningService
from app.api.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/versions", tags=["versioning"])


class CreateVersionRequest(BaseModel):
    change_summary: Optional[str] = None
    version_tag: Optional[str] = None


@router.post("/formulaire/{formulaire_id}")
async def create_version(
    formulaire_id: int,
    data: CreateVersionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une nouvelle version du formulaire"""
    service = VersioningService(db)
    version = await service.create_version(
        formulaire_id=formulaire_id,
        user_id=int(current_user.id),  # type: ignore
        change_summary=data.change_summary,
        version_tag=data.version_tag
    )
    
    return {
        "id": version.id,
        "version_number": version.version_number,
        "version_tag": version.version_tag,
        "created_at": version.created_at.isoformat(),
        "change_summary": version.change_summary
    }


@router.get("/formulaire/{formulaire_id}")
async def get_versions(
    formulaire_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer toutes les versions d'un formulaire"""
    service = VersioningService(db)
    versions = await service.get_versions(formulaire_id)
    
    return {
        "versions": [
            {
                "id": v.id,
                "version_number": v.version_number,
                "version_tag": v.version_tag,
                "created_at": v.created_at.isoformat(),
                "change_summary": v.change_summary,
                "nom": v.nom
            }
            for v in versions
        ]
    }


@router.post("/formulaire/{formulaire_id}/restore/{version_id}")
async def restore_version(
    formulaire_id: int,
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Restaurer une version spécifique"""
    service = VersioningService(db)
    formulaire = await service.restore_version(
        formulaire_id=formulaire_id,
        version_id=version_id,
        user_id=int(current_user.id)  # type: ignore
    )
    
    return {
        "message": "Version restaurée avec succès",
        "formulaire_id": formulaire.id,
        "nom": formulaire.nom
    }


@router.get("/compare/{version_id_1}/{version_id_2}")
async def compare_versions(
    version_id_1: int,
    version_id_2: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Comparer deux versions"""
    service = VersioningService(db)
    comparison = await service.compare_versions(version_id_1, version_id_2)
    return comparison


@router.get("/audit-logs")
async def get_audit_logs(
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    user_id: Optional[int] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les logs d'audit"""
    service = VersioningService(db)
    logs = await service.get_audit_logs(
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        limit=limit
    )
    
    return {
        "logs": [
            {
                "id": log.id,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "action": log.action,
                "username": log.username,
                "timestamp": log.timestamp.isoformat(),
                "metadata": log.audit_metadata,
                "ip_address": log.ip_address
            }
            for log in logs
        ]
    }
