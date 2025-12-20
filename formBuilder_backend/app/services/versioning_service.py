"""
Service pour le versioning et l'audit log
"""
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.versioning import FormulaireVersion, AuditLog
from app.models.formulaire import Formulaire


class VersioningService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_version(
        self,
        formulaire_id: int,
        user_id: int,
        change_summary: Optional[str] = None,
        version_tag: Optional[str] = None
    ) -> FormulaireVersion:
        """Créer une nouvelle version du formulaire"""
        # Récupérer le formulaire actuel
        result = await self.db.execute(
            select(Formulaire).where(Formulaire.id == formulaire_id)
        )
        formulaire = result.scalar_one()
        
        # Compter les versions existantes
        count_result = await self.db.execute(
            select(func.count(FormulaireVersion.id))
            .where(FormulaireVersion.formulaire_id == formulaire_id)
        )
        version_number = (count_result.scalar() or 0) + 1
        
        # Créer la version
        version = FormulaireVersion(
            formulaire_id=formulaire_id,
            version_number=version_number,
            version_tag=version_tag or f"v{version_number}",
            nom=formulaire.nom,
            description=formulaire.description,
            structure_json=formulaire.structure_json,
            type_structurel=formulaire.type_structurel,
            type_fonctionnel=formulaire.type_fonctionnel,
            created_by=user_id,
            change_summary=change_summary
        )
        
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        
        # Log l'action
        await self.log_audit(
            entity_type="formulaire",
            entity_id=formulaire_id,
            action="create_version",
            user_id=user_id,
            metadata={"version_number": version_number, "version_tag": version.version_tag}
        )
        
        return version
    
    async def get_versions(self, formulaire_id: int) -> List[FormulaireVersion]:
        """Récupérer toutes les versions d'un formulaire"""
        result = await self.db.execute(
            select(FormulaireVersion)
            .where(FormulaireVersion.formulaire_id == formulaire_id)
            .order_by(desc(FormulaireVersion.version_number))
        )
        return list(result.scalars().all())
    
    async def restore_version(
        self,
        formulaire_id: int,
        version_id: int,
        user_id: int
    ) -> Formulaire:
        """Restaurer une version spécifique"""
        # Récupérer la version
        version_result = await self.db.execute(
            select(FormulaireVersion).where(FormulaireVersion.id == version_id)
        )
        version = version_result.scalar_one()
        
        # Récupérer le formulaire
        form_result = await self.db.execute(
            select(Formulaire).where(Formulaire.id == formulaire_id)
        )
        formulaire = form_result.scalar_one()
        
        # Sauvegarder l'état actuel avant restauration
        await self.create_version(
            formulaire_id=formulaire_id,
            user_id=user_id,
            change_summary=f"Backup avant restauration de la version {version.version_number}",
            version_tag="backup"
        )
        
        # Restaurer
        formulaire.nom = version.nom
        formulaire.description = version.description
        formulaire.structure_json = version.structure_json
        formulaire.type_structurel = version.type_structurel
        formulaire.type_fonctionnel = version.type_fonctionnel
        
        await self.db.commit()
        await self.db.refresh(formulaire)
        
        # Log l'action
        await self.log_audit(
            entity_type="formulaire",
            entity_id=formulaire_id,
            action="restore_version",
            user_id=user_id,
            metadata={"restored_version": version.version_number}
        )
        
        return formulaire
    
    async def compare_versions(
        self,
        version_id_1: int,
        version_id_2: int
    ) -> Dict:
        """Comparer deux versions"""
        result = await self.db.execute(
            select(FormulaireVersion)
            .where(FormulaireVersion.id.in_([version_id_1, version_id_2]))
        )
        versions = result.scalars().all()
        
        if len(versions) != 2:
            raise ValueError("Les deux versions doivent exister")
        
        v1, v2 = versions[0], versions[1]
        
        return {
            "version_1": {
                "version_number": v1.version_number,
                "nom": v1.nom,
                "created_at": v1.created_at.isoformat(),
                "change_summary": v1.change_summary
            },
            "version_2": {
                "version_number": v2.version_number,
                "nom": v2.nom,
                "created_at": v2.created_at.isoformat(),
                "change_summary": v2.change_summary
            },
            "differences": {
                "nom_changed": v1.nom != v2.nom,
                "description_changed": v1.description != v2.description,
                "structure_changed": v1.structure_json != v2.structure_json
            }
        }
    
    async def log_audit(
        self,
        entity_type: str,
        entity_id: int,
        action: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        changes: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        ip_address: str = "",
        user_agent: str = ""
    ):
        """Enregistrer une entrée d'audit"""
        log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            username=username,
            changes=changes,
            audit_metadata=metadata,  # Renommé pour éviter conflit avec SQLAlchemy
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(log)
        await self.db.commit()
    
    async def get_audit_logs(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Récupérer les logs d'audit avec filtres"""
        query = select(AuditLog)
        
        filters = []
        if entity_type:
            filters.append(AuditLog.entity_type == entity_type)
        if entity_id:
            filters.append(AuditLog.entity_id == entity_id)
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(desc(AuditLog.timestamp)).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())


# Import nécessaire
from sqlalchemy import func, and_
