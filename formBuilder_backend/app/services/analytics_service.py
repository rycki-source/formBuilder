"""
Service pour les analytics et statistiques des formulaires
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.analytics import FormAnalytics, SubmissionEvent, FieldAnalytics
from app.models.soumission import Soumission


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def track_event(
        self,
        formulaire_id: int,
        event_type: str,
        session_id: str,
        user_agent: str = "",
        ip_address: str = "",
        field_name: Optional[str] = None,
        step_number: Optional[int] = None,
        error_message: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        soumission_id: Optional[int] = None
    ):
        """Enregistrer un événement de tracking"""
        event = SubmissionEvent(
            formulaire_id=formulaire_id,
            soumission_id=soumission_id,
            event_type=event_type,
            field_name=field_name,
            step_number=step_number,
            error_message=error_message,
            user_agent=user_agent,
            ip_address=ip_address,
            session_id=session_id,
            duration_seconds=duration_seconds
        )
        
        self.db.add(event)
        await self.db.commit()
        
        # Mettre à jour les analytics agrégées
        await self._update_aggregated_analytics(formulaire_id)
    
    async def _update_aggregated_analytics(self, formulaire_id: int):
        """Mettre à jour les statistiques agrégées"""
        # Récupérer ou créer l'entrée analytics
        result = await self.db.execute(
            select(FormAnalytics).where(FormAnalytics.formulaire_id == formulaire_id)
        )
        analytics = result.scalar_one_or_none()
        
        if not analytics:
            analytics = FormAnalytics(formulaire_id=formulaire_id)
            self.db.add(analytics)
        
        # Compter les événements
        views_result = await self.db.execute(
            select(func.count(SubmissionEvent.id))
            .where(
                and_(
                    SubmissionEvent.formulaire_id == formulaire_id,
                    SubmissionEvent.event_type == 'view'
                )
            )
        )
        analytics.total_views = views_result.scalar() or 0  # type: ignore
        
        # Soumissions
        submissions_result = await self.db.execute(
            select(func.count(Soumission.id))
            .where(Soumission.formulaire_id == formulaire_id)
        )
        analytics.total_submissions = submissions_result.scalar() or 0  # type: ignore
        
        # Complétés
        completed_result = await self.db.execute(
            select(func.count(Soumission.id))
            .where(
                and_(
                    Soumission.formulaire_id == formulaire_id,
                    Soumission.statut == 'VALIDE'
                )
            )
        )
        analytics.total_completed = completed_result.scalar() or 0  # type: ignore
        
        # Calcul du taux de complétion
        if analytics.total_views and analytics.total_views > 0:  # type: ignore
            completion_rate = (analytics.total_completed / analytics.total_views) * 100  # type: ignore
            analytics.completion_rate = completion_rate  # type: ignore
        
        # Temps moyen
        avg_time_result = await self.db.execute(
            select(func.avg(SubmissionEvent.duration_seconds))
            .where(
                and_(
                    SubmissionEvent.formulaire_id == formulaire_id,
                    SubmissionEvent.event_type == 'submit',
                    SubmissionEvent.duration_seconds.isnot(None)
                )
            )
        )
        analytics.average_time_seconds = float(avg_time_result.scalar() or 0.0)  # type: ignore
        
        analytics.last_updated = datetime.now()  # type: ignore
        await self.db.commit()
    
    async def get_dashboard_stats(self, formulaire_id: int) -> Dict:
        """Récupérer les statistiques pour le dashboard"""
        # Analytics agrégées
        result = await self.db.execute(
            select(FormAnalytics).where(FormAnalytics.formulaire_id == formulaire_id)
        )
        analytics = result.scalar_one_or_none()
        
        if not analytics:
            return {
                "total_views": 0,
                "total_submissions": 0,
                "total_completed": 0,
                "completion_rate": 0.0,
                "average_time_seconds": 0.0,
                "trending": []
            }
        
        # Tendances sur les 7 derniers jours
        seven_days_ago = datetime.now() - timedelta(days=7)
        trending_result = await self.db.execute(
            select(
                func.date(SubmissionEvent.timestamp).label('date'),
                func.count(SubmissionEvent.id).label('count')
            )
            .where(
                and_(
                    SubmissionEvent.formulaire_id == formulaire_id,
                    SubmissionEvent.event_type == 'submit',
                    SubmissionEvent.timestamp >= seven_days_ago
                )
            )
            .group_by(func.date(SubmissionEvent.timestamp))
            .order_by(func.date(SubmissionEvent.timestamp))
        )
        
        trending = [
            {"date": str(row.date), "count": row.count}
            for row in trending_result
        ]
        
        return {
            "total_views": analytics.total_views,
            "total_submissions": analytics.total_submissions,
            "total_completed": analytics.total_completed,
            "completion_rate": round(float(analytics.completion_rate or 0), 2),  # type: ignore
            "average_time_seconds": round(float(analytics.average_time_seconds or 0), 2),  # type: ignore
            "trending": trending
        }
    
    async def get_field_analytics(self, formulaire_id: int) -> List[Dict]:
        """Statistiques par champ"""
        result = await self.db.execute(
            select(FieldAnalytics)
            .where(FieldAnalytics.formulaire_id == formulaire_id)
            .order_by(FieldAnalytics.total_errors.desc())
        )
        
        field_stats = result.scalars().all()
        
        return [
            {
                "field_name": fs.field_name,
                "total_filled": fs.total_filled,
                "total_errors": fs.total_errors,
                "average_time_seconds": round(float(fs.average_time_seconds or 0), 2),  # type: ignore
                "common_errors": fs.common_errors or []
            }
            for fs in field_stats
        ]
    
    async def get_abandonment_points(self, formulaire_id: int) -> List[Dict]:
        """Points d'abandon dans le formulaire"""
        result = await self.db.execute(
            select(
                SubmissionEvent.step_number,
                func.count(SubmissionEvent.id).label('abandon_count')
            )
            .where(
                and_(
                    SubmissionEvent.formulaire_id == formulaire_id,
                    SubmissionEvent.event_type == 'abandon',
                    SubmissionEvent.step_number.isnot(None)
                )
            )
            .group_by(SubmissionEvent.step_number)
            .order_by(SubmissionEvent.step_number)
        )
        
        return [
            {"step": row.step_number, "abandons": row.abandon_count}
            for row in result
        ]
