"""Service de gestion des logs d'erreurs"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_, desc
from app.models.error_log import ErrorLog, ErrorSeverity, ErrorType
from app.schemas.error_log import ErrorLogCreate, ErrorLogUpdate, ErrorStats
from typing import Optional, List
from datetime import datetime, timedelta


class ErrorLogService:
    """Service pour gérer les logs d'erreurs"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_error_log(self, error_data: ErrorLogCreate) -> ErrorLog:
        """Créer un nouveau log d'erreur"""
        error_log = ErrorLog(**error_data.model_dump())
        self.db.add(error_log)
        await self.db.commit()
        await self.db.refresh(error_log)
        return error_log

    async def get_error_log(self, error_id: int, include_stack_trace: bool = False) -> Optional[ErrorLog]:
        """Récupérer un log d'erreur par ID"""
        result = await self.db.execute(
            select(ErrorLog).where(ErrorLog.id == error_id)
        )
        error_log = result.scalar_one_or_none()
        
        # Masquer le stack trace si non demandé (pour la sécurité)
        if error_log and not include_stack_trace:
            # Masquer stack trace
            setattr(error_log, 'stack_trace', '')
            
        return error_log

    async def list_error_logs(
        self,
        type_erreur: Optional[ErrorType] = None,
        severite: Optional[ErrorSeverity] = None,
        resolu: Optional[bool] = None,
        user_id: Optional[int] = None,
        endpoint: Optional[str] = None,
        date_debut: Optional[datetime] = None,
        date_fin: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[ErrorLog], int]:
        """Lister les logs d'erreurs avec filtres"""
        query = select(ErrorLog)
        conditions = []

        if type_erreur:
            conditions.append(ErrorLog.type_erreur == type_erreur)
        if severite:
            conditions.append(ErrorLog.severite == severite)
        if resolu is not None:
            conditions.append(ErrorLog.resolu == resolu)
        if user_id:
            conditions.append(ErrorLog.user_id == user_id)
        if endpoint:
            conditions.append(ErrorLog.endpoint.ilike(f"%{endpoint}%"))
        if date_debut:
            conditions.append(ErrorLog.date_erreur >= date_debut)
        if date_fin:
            conditions.append(ErrorLog.date_erreur <= date_fin)

        if conditions:
            query = query.where(and_(*conditions))

        # Total
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()

        # Pagination et tri
        query = query.order_by(desc(ErrorLog.date_erreur))
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        
        # Retourner les erreurs directement
        errors = list(result.scalars().all())

        return errors, total or 0

    async def update_error_log(self, error_id: int, error_data: ErrorLogUpdate) -> Optional[ErrorLog]:
        """Mettre à jour un log d'erreur"""
        error_log = await self.get_error_log(error_id, include_stack_trace=True)
        if not error_log:
            return None

        for key, value in error_data.model_dump(exclude_unset=True).items():
            setattr(error_log, key, value)

        if error_data.resolu and error_log.date_resolution is None:
            setattr(error_log, 'date_resolution', datetime.utcnow())

        await self.db.commit()
        await self.db.refresh(error_log)
        return error_log

    async def mark_as_resolved(self, error_id: int, notes: Optional[str] = None) -> Optional[ErrorLog]:
        """Marquer une erreur comme résolue"""
        return await self.update_error_log(
            error_id,
            ErrorLogUpdate(resolu=True, notes=notes)
        )

    async def delete_error_log(self, error_id: int) -> bool:
        """Supprimer un log d'erreur"""
        error_log = await self.get_error_log(error_id, include_stack_trace=True)
        if not error_log:
            return False

        await self.db.delete(error_log)
        await self.db.commit()
        return True

    async def get_stats(self) -> ErrorStats:
        """Obtenir les statistiques des erreurs"""
        # Total
        total_result = await self.db.execute(select(func.count(ErrorLog.id)))
        total = total_result.scalar()

        # Non résolues
        non_resolus_result = await self.db.execute(
            select(func.count()).where(ErrorLog.resolu == False)
        )
        non_resolus = non_resolus_result.scalar()

        # Par type
        par_type = {}
        for error_type in ErrorType:
            count_result = await self.db.execute(
                select(func.count()).where(ErrorLog.type_erreur == error_type)
            )
            count = count_result.scalar()
            if count is not None:
                par_type[error_type.value] = count

        # Par sévérité
        par_severite = {}
        for severity in ErrorSeverity:
            count_result = await self.db.execute(
                select(func.count()).where(ErrorLog.severite == severity)
            )
            count = count_result.scalar()
            par_severite[severity.value] = count or 0

        # Dernières 24h
        now = datetime.utcnow()
        date_24h = now - timedelta(hours=24)
        derniere_24h_result = await self.db.execute(
            select(func.count()).where(ErrorLog.date_erreur >= date_24h)
        )
        derniere_24h = derniere_24h_result.scalar()

        return ErrorStats(
            total=total or 0,
            non_resolus=non_resolus or 0,
            par_type=par_type,
            par_severite=par_severite,
            derniere_24h=derniere_24h or 0
        )

    async def cleanup_old_errors(self, days: int = 90) -> int:
        """Nettoyer les anciens logs d'erreurs résolus"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(ErrorLog).where(
                and_(
                    ErrorLog.resolu == True,
                    ErrorLog.date_erreur < cutoff_date
                )
            )
        )
        old_errors = result.scalars().all()

        count = 0
        for error in old_errors:
            await self.db.delete(error)
            count += 1

        if count > 0:
            await self.db.commit()

        return count
