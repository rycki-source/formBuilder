"""Endpoints API pour l'audit des actions administratives"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.admin_audit import AdminAuditCreate, AdminAuditResponse, AdminAuditStats
from app.services.admin_audit_service import AdminAuditService

router = APIRouter(prefix="/admin/audit", tags=["Admin - Audit"])


@router.get("/", response_model=dict)
async def list_audit_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    success: Optional[bool] = Query(None),
    date_debut: Optional[datetime] = Query(None),
    date_fin: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister les logs d'audit avec pagination et filtres"""
    # TODO: Vérifier permission admin
    service = AdminAuditService(db)
    skip = (page - 1) * page_size
    
    logs, total = await service.list_audit_logs(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        success=success,
        date_debut=date_debut,
        date_fin=date_fin,
        skip=skip,
        limit=page_size
    )
    
    return {
        "items": logs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/stats", response_model=AdminAuditStats)
async def get_audit_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir les statistiques d'audit"""
    # TODO: Vérifier permission admin
    service = AdminAuditService(db)
    return await service.get_stats()


@router.get("/{audit_id}", response_model=AdminAuditResponse)
async def get_audit_log(
    audit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un log d'audit par ID"""
    # TODO: Vérifier permission admin
    service = AdminAuditService(db)
    log = await service.get_audit_log(audit_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log d'audit non trouvé")
    return log


@router.post("/cleanup-old", response_model=dict)
async def cleanup_old_logs(
    days: int = Query(180, ge=90, le=730),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Nettoyer les anciens logs d'audit"""
    # TODO: Vérifier permission super-admin
    service = AdminAuditService(db)
    count = await service.cleanup_old_logs(days)
    return {"cleaned_count": count}
