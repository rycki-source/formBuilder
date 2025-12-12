"""Endpoints API pour la gestion des alertes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.admin_alert import AlertStatus, AlertType
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse, AlertStats
from app.services.alert_service import AlertService

router = APIRouter(prefix="/admin/alerts", tags=["Admin - Alertes"])


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une nouvelle alerte"""
    service = AlertService(db)
    alert = await service.create_alert(alert_data)
    return alert


@router.get("/", response_model=dict)
async def list_alerts(
    statut: Optional[AlertStatus] = Query(None),
    type_alert: Optional[AlertType] = Query(None),
    lu: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister les alertes avec pagination et filtres"""
    service = AlertService(db)
    skip = (page - 1) * page_size
    
    alerts, total = await service.list_alerts(
        statut=statut,
        type_alert=type_alert,
        lu=lu,
        utilisateur_id=getattr(current_user, 'id', None),
        skip=skip,
        limit=page_size
    )
    
    return {
        "items": alerts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/stats", response_model=AlertStats)
async def get_alert_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir les statistiques des alertes"""
    service = AlertService(db)
    return await service.get_stats()


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer une alerte par ID"""
    service = AlertService(db)
    alert = await service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour une alerte"""
    service = AlertService(db)
    alert = await service.update_alert(alert_id, alert_data)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return alert


@router.post("/{alert_id}/mark-read", response_model=AlertResponse)
async def mark_alert_as_read(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marquer une alerte comme lue"""
    service = AlertService(db)
    alert = await service.mark_as_read(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return alert


@router.post("/mark-multiple-read", response_model=dict)
async def mark_multiple_alerts_as_read(
    alert_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marquer plusieurs alertes comme lues"""
    service = AlertService(db)
    count = await service.mark_multiple_as_read(alert_ids)
    return {"marked_count": count}


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer une alerte (archivage)"""
    service = AlertService(db)
    success = await service.delete_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")


@router.post("/cleanup-expired", response_model=dict)
async def cleanup_expired_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Nettoyer les alertes expirées"""
    # TODO: Vérifier permission admin
    service = AlertService(db)
    count = await service.cleanup_expired()
    return {"cleaned_count": count}
