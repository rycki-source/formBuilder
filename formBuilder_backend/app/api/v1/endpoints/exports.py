"""Endpoints pour les exports"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from app.api.dependencies import get_current_user
from app.schemas.soumission import ExportRequest
from app.utils.excel_handler import ExcelHandler
from app.utils.pdf_generator import PDFGenerator
import csv
import json
import tempfile
from typing import List

router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("/")
async def export_soumissions(
    export_request: ExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Exporter les soumissions"""
    if not export_request.soumission_ids:
        raise HTTPException(status_code=400, detail="Aucune soumission sélectionnée")
    
    format_type = export_request.format.lower()

    if format_type == "csv":
        return await _export_csv(export_request.soumission_ids, db)
    elif format_type == "excel":
        return await _export_excel(export_request.soumission_ids, db)
    elif format_type == "json":
        return await _export_json(export_request.soumission_ids, db)
    else:
        raise HTTPException(status_code=400, detail="Format non supporté")


async def _export_csv(soumission_ids: List[int], db: AsyncSession) -> FileResponse:
    """Exporter en CSV"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        # Logic pour exporter
        f.flush()
        return FileResponse(f.name, media_type="text/csv")


async def _export_excel(soumission_ids: List[int], db: AsyncSession) -> FileResponse:
    """Exporter en Excel"""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        # Logic pour exporter
        f.flush()
        return FileResponse(
            f.name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


async def _export_json(soumission_ids: List[int], db: AsyncSession) -> FileResponse:
    """Exporter en JSON"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        # Logic pour exporter
        f.flush()
        return FileResponse(f.name, media_type="application/json")
