"""Service pour les soumissions"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.soumission import Soumission, ValidationSoumission, RapportValidation
from app.services.validation_service import ValidationService
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime


class SoumissionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_soumission(
        self,
        formulaire_id: int,
        donnees: Dict[str, Any],
        utilisateur_id: int,
        version: str,
    ) -> Soumission:
        """Créer une soumission"""
        new_soumission = Soumission(
            formulaire_id=formulaire_id,
            donnees=donnees,
            utilisateur_id=utilisateur_id,
            version_formulaire=version,
            statut="SOUMIS",
        )
        self.db.add(new_soumission)
        await self.db.commit()
        await self.db.refresh(new_soumission)
        return new_soumission

    async def get_soumission(self, soumission_id: int) -> Optional[Soumission]:
        """Récupérer une soumission"""
        result = await self.db.execute(
            select(Soumission).where(Soumission.id == soumission_id)
        )
        return result.scalar_one_or_none()

    async def list_soumissions(
        self, formulaire_id: Optional[int] = None, skip: int = 0, limit: int = 10
    ) -> List[Soumission]:
        """Lister les soumissions"""
        query = select(Soumission)
        if formulaire_id:
            query = query.where(Soumission.formulaire_id == formulaire_id)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_soumission_status(
        self, soumission_id: int, statut: str
    ) -> Optional[Soumission]:
        """Mettre à jour le statut d'une soumission"""
        soumission = await self.get_soumission(soumission_id)
        if not soumission:
            return None

        setattr(soumission, "statut", statut)  # type: ignore[assignment]
        await self.db.commit()
        await self.db.refresh(soumission)
        return soumission
