"""Endpoints API pour la gestion des logs d'erreurs"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.error_log import ErrorSeverity, ErrorType
from app.schemas.error_log import (
    ErrorLogCreate, ErrorLogUpdate, ErrorLogResponse,
    ErrorLogListResponse, ErrorStats
)
from app.services.error_log_service import ErrorLogService

router = APIRouter(prefix="/admin/errors", tags=["Admin - Erreurs"])


@router.post("/", response_model=ErrorLogResponse, status_code=201)
async def create_error_log(
    error_data: ErrorLogCreate,
    db: AsyncSession = Depends(get_db)
):
    """Créer un nouveau log d'erreur (endpoint public pour logging)"""
    service = ErrorLogService(db)
    error_log = await service.create_error_log(error_data)
    return error_log


@router.get("/", response_model=dict)
async def list_error_logs(
    type_erreur: Optional[ErrorType] = Query(None),
    severite: Optional[ErrorSeverity] = Query(None),
    resolu: Optional[bool] = Query(None),
    endpoint: Optional[str] = Query(None),
    date_debut: Optional[datetime] = Query(None),
    date_fin: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister les logs d'erreurs avec pagination et filtres"""
    service = ErrorLogService(db)
    skip = (page - 1) * page_size
    
    errors, total = await service.list_error_logs(
        type_erreur=type_erreur,
        severite=severite,
        resolu=resolu,
        endpoint=endpoint,
        date_debut=date_debut,
        date_fin=date_fin,
        skip=skip,
        limit=page_size
    )
    
    return {
        "items": errors,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/stats", response_model=ErrorStats)
async def get_error_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir les statistiques des erreurs"""
    service = ErrorLogService(db)
    return await service.get_stats()


@router.get("/{error_id}", response_model=ErrorLogResponse)
async def get_error_log(
    error_id: int,
    include_stack_trace: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un log d'erreur par ID (avec stack trace si demandé)"""
    # TODO: Vérifier permission pour stack trace
    service = ErrorLogService(db)
    error_log = await service.get_error_log(error_id, include_stack_trace)
    if not error_log:
        raise HTTPException(status_code=404, detail="Log d'erreur non trouvé")
    return error_log


@router.patch("/{error_id}", response_model=ErrorLogResponse)
async def update_error_log(
    error_id: int,
    error_data: ErrorLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un log d'erreur"""
    service = ErrorLogService(db)
    error_log = await service.update_error_log(error_id, error_data)
    if not error_log:
        raise HTTPException(status_code=404, detail="Log d'erreur non trouvé")
    return error_log


@router.post("/{error_id}/resolve", response_model=ErrorLogResponse)
async def mark_error_as_resolved(
    error_id: int,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marquer une erreur comme résolue"""
    service = ErrorLogService(db)
    error_log = await service.mark_as_resolved(error_id, notes)
    if not error_log:
        raise HTTPException(status_code=404, detail="Log d'erreur non trouvé")
    return error_log


@router.delete("/{error_id}", status_code=204)
async def delete_error_log(
    error_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un log d'erreur"""
    # TODO: Vérifier permission admin
    service = ErrorLogService(db)
    success = await service.delete_error_log(error_id)
    if not success:
        raise HTTPException(status_code=404, detail="Log d'erreur non trouvé")


@router.post("/cleanup-old", response_model=dict)
async def cleanup_old_errors(
    days: int = Query(90, ge=30, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Nettoyer les anciens logs d'erreurs résolus"""
    # TODO: Vérifier permission admin
    service = ErrorLogService(db)
    count = await service.cleanup_old_errors(days)
    return {"cleaned_count": count}
