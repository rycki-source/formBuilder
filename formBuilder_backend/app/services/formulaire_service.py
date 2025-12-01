from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.formulaire import Formulaire, FormulaireVersion
from app.schemas.formulaire import FormulaireCreate, FormulaireUpdate
from typing import List, Optional
from datetime import datetime
import json


class FormulaireService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_formulaire(
        self, form_data: FormulaireCreate, developpeur_id: int
    ) -> Formulaire:
        """Créer un nouveau formulaire"""
        new_form = Formulaire(
            nom=form_data.nom,
            description=form_data.description,
            structure_json=form_data.structure_json,
            developpeur_id=developpeur_id,
        )
        self.db.add(new_form)
        await self.db.commit()
        await self.db.refresh(new_form)

        # Créer la version 1.0
        version = FormulaireVersion(
            formulaire_id=new_form.id,
            numero_version="1.0",
            majeur=1,
            mineur=0,
            patch=0,
            structure_json=form_data.structure_json,
            auteur_id=developpeur_id,
        )
        self.db.add(version)
        await self.db.commit()

        return new_form

    async def get_formulaire(self, formulaire_id: int) -> Optional[Formulaire]:
        """Récupérer un formulaire"""
        result = await self.db.execute(
            select(Formulaire).where(Formulaire.id == formulaire_id)
        )
        return result.scalar_one_or_none()

    async def list_formulaires(
        self, skip: int = 0, limit: int = 10
    ) -> List[Formulaire]:
        """Lister les formulaires"""
        result = await self.db.execute(
            select(Formulaire).where(Formulaire.actif == True).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def list_user_formulaires(self, user_id: int, skip: int = 0, limit: int = 10) -> List[Formulaire]:
        """Liste les formulaires d'un utilisateur spécifique"""
        result = await self.db.execute(
            select(Formulaire)
            .where(Formulaire.developpeur_id == user_id, Formulaire.actif == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_formulaire(
        self, formulaire_id: int, form_data: FormulaireUpdate
    ) -> Optional[Formulaire]:
        """Mettre à jour un formulaire"""
        formulaire = await self.get_formulaire(formulaire_id)
        if not formulaire:
            return None

        if form_data.nom:
            setattr(formulaire, "nom", form_data.nom)
        if form_data.description is not None:
            setattr(formulaire, "description", form_data.description)
        if form_data.structure_json:
            setattr(formulaire, "structure_json", form_data.structure_json)

        setattr(formulaire, "date_modification", datetime.utcnow())
        await self.db.commit()
        await self.db.refresh(formulaire)
        return formulaire

    async def publish_formulaire(self, formulaire_id: int) -> Optional[Formulaire]:
        """Publier un formulaire"""
        formulaire = await self.get_formulaire(formulaire_id)
        if not formulaire:
            return None

        setattr(formulaire, "publie", True)
        await self.db.commit()
        await self.db.refresh(formulaire)
        return formulaire

    async def delete_formulaire(self, formulaire_id: int) -> bool:
        """Supprimer un formulaire (soft delete)"""
        formulaire = await self.get_formulaire(formulaire_id)
        if not formulaire:
            return False

        setattr(formulaire, "actif", False)
        await self.db.commit()
        return True
