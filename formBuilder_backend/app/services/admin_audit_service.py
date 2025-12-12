"""Service de gestion de l'audit log administratif"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from app.models.admin_audit import AdminAudit
from app.schemas.admin_audit import AdminAuditCreate, AdminAuditStats
from typing import Optional, List
from datetime import datetime, timedelta


class AdminAuditService:
    """Service pour gérer l'audit log des actions administratives"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(self, audit_data: AdminAuditCreate) -> AdminAudit:
        """Enregistrer une action administrative"""
        audit = AdminAudit(**audit_data.model_dump())
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(audit)
        return audit

    async def get_audit_log(self, audit_id: int) -> Optional[AdminAudit]:
        """Récupérer un log d'audit par ID"""
        result = await self.db.execute(
            select(AdminAudit).where(AdminAudit.id == audit_id)
        )
        return result.scalar_one_or_none()

    async def list_audit_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        success: Optional[bool] = None,
        date_debut: Optional[datetime] = None,
        date_fin: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[AdminAudit], int]:
        """Lister les logs d'audit avec filtres"""
        query = select(AdminAudit)
        conditions = []

        if user_id:
            conditions.append(AdminAudit.user_id == user_id)
        if action:
            conditions.append(AdminAudit.action.ilike(f"%{action}%"))
        if resource_type:
            conditions.append(AdminAudit.resource_type == resource_type)
        if success is not None:
            conditions.append(AdminAudit.success == success)
        if date_debut:
            conditions.append(AdminAudit.date_action >= date_debut)
        if date_fin:
            conditions.append(AdminAudit.date_action <= date_fin)

        if conditions:
            query = query.where(and_(*conditions))

        # Total
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()

        # Pagination et tri
        query = query.order_by(desc(AdminAudit.date_action))
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total or 0

    async def get_stats(self) -> AdminAuditStats:
        """Obtenir les statistiques de l'audit"""
        # Total d'actions
        total_result = await self.db.execute(select(func.count(AdminAudit.id)))
        total_actions = total_result.scalar()

        # Actions réussies
        reussies_result = await self.db.execute(
            select(func.count()).where(AdminAudit.success == True)
        )
        actions_reussies = reussies_result.scalar()

        # Actions échouées
        echouees_result = await self.db.execute(
            select(func.count()).where(AdminAudit.success == False)
        )
        actions_echouees = echouees_result.scalar()

        # Par type de ressource
        types_result = await self.db.execute(
            select(AdminAudit.resource_type, func.count(AdminAudit.id))
            .group_by(AdminAudit.resource_type)
        )
        par_type = {row[0]: row[1] for row in types_result.all()}

        # Dernières 24h
        now = datetime.utcnow()
        date_24h = now - timedelta(hours=24)
        derniere_24h_result = await self.db.execute(
            select(func.count()).where(AdminAudit.date_action >= date_24h)
        )
        derniere_24h = derniere_24h_result.scalar()

        return AdminAuditStats(
            total_actions=total_actions or 0,
            actions_reussies=actions_reussies or 0,
            actions_echouees=actions_echouees or 0,
            par_type=par_type,
            derniere_24h=derniere_24h or 0
        )

    async def cleanup_old_logs(self, days: int = 180) -> int:
        """Nettoyer les anciens logs d'audit"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(AdminAudit).where(AdminAudit.date_action < cutoff_date)
        )
        old_logs = result.scalars().all()

        count = 0
        for log in old_logs:
            await self.db.delete(log)
            count += 1

        if count > 0:
            await self.db.commit()

        return count
