"""Service pour les référentiels"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.referentiel import Referentiel, ReferentielDonnees
from typing import Optional, List, Dict, Any
from datetime import datetime


class ReferentielService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_referentiel(
        self,
        nom: str,
        source_type: str,
        metadata_json: Dict[str, Any],
        personne_import_id: int,
    ) -> Referentiel:
        """Créer un référentiel"""
        new_ref = Referentiel(
            nom=nom,
            source_type=source_type,
            metadata_json=metadata_json,
            personne_import_id=personne_import_id,
            valide=True,
        )
        self.db.add(new_ref)
        await self.db.commit()
        await self.db.refresh(new_ref)
        return new_ref

    async def get_referentiel(self, referentiel_id: int) -> Optional[Referentiel]:
        """Récupérer un référentiel"""
        result = await self.db.execute(
            select(Referentiel).where(Referentiel.id == referentiel_id)
        )
        return result.scalar_one_or_none()

    async def list_referentiels(
        self, skip: int = 0, limit: int = 10
    ) -> List[Referentiel]:
        """Lister les référentiels"""
        result = await self.db.execute(select(Referentiel).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def add_referentiel_data(
        self, referentiel_id: int, donnees: List[Dict[str, Any]]
    ):
        """Ajouter des données à un référentiel"""
        for item in donnees:
            ref_data = ReferentielDonnees(
                referentiel_id=referentiel_id, cle=item.get("cle"), valeur=item
            )
            self.db.add(ref_data)
        await self.db.commit()
