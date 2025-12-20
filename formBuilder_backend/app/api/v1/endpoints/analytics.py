"""
Endpoints pour les analytics et statistiques
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.analytics_service import AnalyticsService
from app.api.dependencies import get_current_user
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/formulaire/{formulaire_id}/dashboard")
async def get_dashboard_stats(
    formulaire_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les statistiques du dashboard pour un formulaire"""
    service = AnalyticsService(db)
    stats = await service.get_dashboard_stats(formulaire_id)
    return stats


@router.get("/formulaire/{formulaire_id}/fields")
async def get_field_analytics(
    formulaire_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les statistiques par champ"""
    service = AnalyticsService(db)
    field_stats = await service.get_field_analytics(formulaire_id)
    return {"fields": field_stats}


@router.get("/formulaire/{formulaire_id}/abandonment")
async def get_abandonment_points(
    formulaire_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les points d'abandon dans le formulaire"""
    service = AnalyticsService(db)
    abandonment = await service.get_abandonment_points(formulaire_id)
    return {"abandonment_points": abandonment}


@router.post("/track")
async def track_event(
    formulaire_id: int,
    event_type: str,
    session_id: str,
    request: Request,
    field_name: Optional[str] = None,
    step_number: Optional[int] = None,
    error_message: Optional[str] = None,
    duration_seconds: Optional[float] = None,
    soumission_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Enregistrer un événement de tracking (public pour le frontend)"""
    service = AnalyticsService(db)
    
    # Récupérer IP et user agent
    ip_address = request.client.host if request.client else ""
    user_agent = request.headers.get("user-agent", "")
    
    await service.track_event(
        formulaire_id=formulaire_id,
        event_type=event_type,
        session_id=session_id,
        user_agent=user_agent,
        ip_address=ip_address,
        field_name=field_name,
        step_number=step_number,
        error_message=error_message,
        duration_seconds=duration_seconds,
        soumission_id=soumission_id
    )
    
    return {"status": "tracked"}
