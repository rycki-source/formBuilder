"""Endpoints pour les référentiels"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from app.services.referentiel_service import ReferentielService
from app.api.dependencies import get_current_user
from app.utils.excel_handler import ExcelHandler
from typing import List
import tempfile
import os

router = APIRouter(prefix="/referentiels", tags=["referentiels"])


@router.post("/import")
async def import_referentiel(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Importer un référentiel depuis Excel"""
    try:
        # Sauvegarder le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        # Lire le fichier Excel
        data = ExcelHandler.read_excel(temp_path)

        # Créer le référentiel
        service = ReferentielService(db)
        referentiel = await service.create_referentiel(
            nom=(file.filename or "referentiel").replace(".xlsx", ""),
            source_type="EXCEL",
            metadata_json={"sheets": list(data.keys())},
            personne_import_id=getattr(current_user, 'id'),
        )

        # Ajouter les données
        for sheet_name, rows in data.items():
            for row in rows:
                await service.add_referentiel_data(getattr(referentiel, 'id'), [row])

        # Supprimer le fichier temporaire
        os.unlink(temp_path)

        return {"message": "Référentiel importé", "referentiel_id": referentiel.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def list_referentiels(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les référentiels"""
    service = ReferentielService(db)
    referentiels = await service.list_referentiels(skip, limit)
    return referentiels
