"""Service de gestion des alertes admin"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from app.models.admin_alert import Alert, AlertStatus, AlertType
from app.schemas.alert import AlertCreate, AlertUpdate, AlertStats
from typing import Optional, List
from datetime import datetime


class AlertService:
    """Service pour gérer les alertes administratives"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_alert(self, alert_data: AlertCreate) -> Alert:
        """Créer une nouvelle alerte"""
        alert = Alert(**alert_data.model_dump())
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def get_alert(self, alert_id: int) -> Optional[Alert]:
        """Récupérer une alerte par ID"""
        result = await self.db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        return result.scalar_one_or_none()

    async def list_alerts(
        self,
        statut: Optional[AlertStatus] = None,
        type_alert: Optional[AlertType] = None,
        lu: Optional[bool] = None,
        utilisateur_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Alert], int]:
        """Lister les alertes avec filtres"""
        query = select(Alert)
        conditions = []

        if statut:
            conditions.append(Alert.statut == statut)
        if type_alert:
            conditions.append(Alert.type_alert == type_alert)
        if lu is not None:
            conditions.append(Alert.lu == lu)
        if utilisateur_id:
            conditions.append(
                or_(Alert.utilisateur_id == utilisateur_id, Alert.utilisateur_id.is_(None))
            )

        if conditions:
            query = query.where(and_(*conditions))

        # Total
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Pagination et tri
        query = query.order_by(Alert.date_creation.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        alerts = list(result.scalars().all())

        return alerts, total

    async def update_alert(self, alert_id: int, alert_data: AlertUpdate) -> Optional[Alert]:
        """Mettre à jour une alerte"""
        alert = await self.get_alert(alert_id)
        if not alert:
            return None

        for key, value in alert_data.model_dump(exclude_unset=True).items():
            setattr(alert, key, value)

        if alert_data.lu and alert.date_lecture is None:
            setattr(alert, 'date_lecture', datetime.utcnow())

        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def mark_as_read(self, alert_id: int) -> Optional[Alert]:
        """Marquer une alerte comme lue"""
        return await self.update_alert(alert_id, AlertUpdate(lu=True))

    async def mark_all_as_read(self, utilisateur_id: Optional[int] = None) -> int:
        """Marquer toutes les alertes comme lues"""
        query = select(Alert).where(Alert.lu == False)
        
        if utilisateur_id:
            query = query.where(
                or_(Alert.utilisateur_id == utilisateur_id, Alert.utilisateur_id.is_(None))
            )
        
        result = await self.db.execute(query)
        alerts = result.scalars().all()
        
        count = 0
        for alert in alerts:
            setattr(alert, 'lu', True)
            setattr(alert, 'date_lecture', datetime.utcnow())
            count += 1
        
        await self.db.commit()
        return count

    async def mark_multiple_as_read(self, alert_ids: List[int]) -> int:
        """Marquer plusieurs alertes comme lues"""
        if not alert_ids:
            return 0
        
        result = await self.db.execute(
            select(Alert).where(Alert.id.in_(alert_ids))
        )
        alerts = result.scalars().all()
        
        count = 0
        for alert in alerts:
            setattr(alert, 'lu', True)
            setattr(alert, 'date_lecture', datetime.utcnow())
            count += 1
        
        await self.db.commit()
        return count

    async def delete_alert(self, alert_id: int) -> bool:
        """Supprimer une alerte"""
        alert = await self.get_alert(alert_id)
        if not alert:
            return False

        await self.db.delete(alert)
        await self.db.commit()
        return True

    async def get_stats(self, utilisateur_id: Optional[int] = None) -> AlertStats:
        """Obtenir des statistiques sur les alertes"""
        # Total
        query_total = select(func.count()).select_from(Alert)
        if utilisateur_id:
            query_total = query_total.where(
                or_(Alert.utilisateur_id == utilisateur_id, Alert.utilisateur_id.is_(None))
            )
        result_total = await self.db.execute(query_total)
        total = result_total.scalar() or 0

        # Non lues
        query_non_lues = select(func.count()).where(Alert.lu == False)
        if utilisateur_id:
            query_non_lues = query_non_lues.where(
                or_(Alert.utilisateur_id == utilisateur_id, Alert.utilisateur_id.is_(None))
            )
        result_non_lues = await self.db.execute(query_non_lues)
        non_lues = result_non_lues.scalar() or 0

        # Par statut
        par_statut = {}
        for status in AlertStatus:
            query_status = select(func.count()).where(Alert.statut == status)
            if utilisateur_id:
                query_status = query_status.where(
                    or_(Alert.utilisateur_id == utilisateur_id, Alert.utilisateur_id.is_(None))
                )
            result_status = await self.db.execute(query_status)
            par_statut[status.value] = result_status.scalar() or 0

        # Par type
        par_type = {}
        for type_alert in AlertType:
            query_type = select(func.count()).where(Alert.type_alert == type_alert)
            if utilisateur_id:
                query_type = query_type.where(
                    or_(Alert.utilisateur_id == utilisateur_id, Alert.utilisateur_id.is_(None))
                )
            result_type = await self.db.execute(query_type)
            par_type[type_alert.value] = result_type.scalar() or 0

        return AlertStats(
            total=total,
            non_lues=non_lues,
            par_statut=par_statut,
            par_type=par_type
        )

    async def cleanup_expired(self) -> int:
        """Nettoyer les alertes expirées"""
        now = datetime.utcnow()
        query = select(Alert).where(
            and_(
                Alert.date_expiration.isnot(None),
                Alert.date_expiration < now
            )
        )
        
        result = await self.db.execute(query)
        expired = result.scalars().all()
        
        count = 0
        for alert in expired:
            await self.db.delete(alert)
            count += 1
        
        await self.db.commit()
        return count
