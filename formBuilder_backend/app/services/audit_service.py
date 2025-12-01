from sqlalchemy.ext.asyncio import AsyncSession
from app.models.auditLog import AuditLog
from typing import Optional, Dict, Any
from datetime import datetime


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        action: str,
        module: str,
        utilisateur_id: Optional[int] = None,
        ressource_type: Optional[str] = None,
        ressource_id: Optional[int] = None,
        ip_adresse: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        resultat: str = "SUCCESS",
    ) -> AuditLog:
        """Enregistrer une action d'audit"""
        audit_entry = AuditLog(
            utilisateur_id=utilisateur_id,
            action=action,
            module=module,
            ip=ip_adresse,
            details=details,
            resultat={"status": resultat},
            date_action=datetime.utcnow(),
        )
        self.db.add(audit_entry)
        await self.db.commit()
        await self.db.refresh(audit_entry)
        return audit_entry
