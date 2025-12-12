"""Endpoints pour les exports"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.models.soumission import Soumission
from app.models.formulaire import Formulaire
from app.api.dependencies import get_current_user
from app.schemas.soumission import ExportRequest
from app.utils.excel_handler import ExcelHandler
# from app.utils.pdf_generator import PDFGenerator  # Temporairement désactivé (nécessite GTK sur Windows)
import csv
import json
import tempfile
import io
from typing import List
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

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


async def _export_csv(soumission_ids: List[int], db: AsyncSession) -> StreamingResponse:
    """Exporter en CSV"""
    # Récupérer les soumissions
    result = await db.execute(
        select(Soumission).where(Soumission.id.in_(soumission_ids))
    )
    soumissions = result.scalars().all()
    
    if not soumissions:
        raise HTTPException(status_code=404, detail="Aucune soumission trouvée")
    
    # Créer le CSV en mémoire
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    headers = ["ID", "Formulaire", "Date", "Statut", "Utilisateur"]
    # Extraire tous les champs possibles des données
    all_fields = set()
    for soumission in soumissions:
        if isinstance(soumission.donnees, dict):
            all_fields.update(soumission.donnees.keys())
    headers.extend(sorted(all_fields))
    writer.writerow(headers)
    
    # Données
    for soumission in soumissions:
        row = [
            soumission.id,
            soumission.formulaire_id,
            soumission.date_soumission.strftime("%Y-%m-%d %H:%M:%S") if soumission.date_soumission else "",
            soumission.statut,
            soumission.utilisateur_id or "Anonyme"
        ]
        # Ajouter les valeurs des champs
        for field in sorted(all_fields):
            value = soumission.donnees.get(field, "") if isinstance(soumission.donnees, dict) else ""
            # Formater les données complexes
            if isinstance(value, dict):
                # Géolocalisation: afficher comme "lat, lng (accuracy m)"
                if "latitude" in value and "longitude" in value:
                    lat = value.get("latitude")
                    lng = value.get("longitude")
                    acc = value.get("accuracy")
                    value = f"{lat}, {lng}" + (f" (±{acc}m)" if acc else "")
                else:
                    value = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, list):
                value = json.dumps(value, ensure_ascii=False)
            # Signature: indiquer seulement qu'elle existe
            if isinstance(value, str) and value.startswith("data:image/"):
                value = "[Signature image]"
            row.append(value)
        writer.writerow(row)
    
    # Préparer la réponse
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=soumissions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


async def _export_excel(soumission_ids: List[int], db: AsyncSession) -> StreamingResponse:
    """Exporter en Excel"""
    # Récupérer les soumissions avec leurs formulaires
    result = await db.execute(
        select(Soumission).where(Soumission.id.in_(soumission_ids))
    )
    soumissions = result.scalars().all()
    
    if not soumissions:
        raise HTTPException(status_code=404, detail="Aucune soumission trouvée")
    
    # Créer un classeur Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Soumissions"
    
    # Style des en-têtes
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    # En-têtes
    headers = ["ID", "Formulaire", "Date de soumission", "Statut", "Utilisateur", "Version"]
    
    # Extraire tous les champs possibles des données
    all_fields = set()
    for soumission in soumissions:
        if isinstance(soumission.donnees, dict):
            all_fields.update(soumission.donnees.keys())
    
    headers.extend(sorted(all_fields))
    
    # Écrire les en-têtes
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
    
    # Écrire les données
    for row_num, soumission in enumerate(soumissions, 2):
        ws.cell(row=row_num, column=1).value = soumission.id
        ws.cell(row=row_num, column=2).value = soumission.formulaire_id
        ws.cell(row=row_num, column=3).value = soumission.date_soumission.strftime("%Y-%m-%d %H:%M:%S") if soumission.date_soumission else ""
        ws.cell(row=row_num, column=4).value = soumission.statut
        ws.cell(row=row_num, column=5).value = soumission.utilisateur_id or "Anonyme"
        
        # Ajouter les valeurs des champs
        for col_num, field in enumerate(sorted(all_fields), 7):
            value = soumission.donnees.get(field, "") if isinstance(soumission.donnees, dict) else ""
            # Formater les données complexes
            if isinstance(value, dict):
                # Géolocalisation: afficher comme "lat, lng (accuracy m)"
                if "latitude" in value and "longitude" in value:
                    lat = value.get("latitude")
                    lng = value.get("longitude")
                    acc = value.get("accuracy")
                    value = f"{lat}, {lng}" + (f" (±{acc}m)" if acc else "")
                else:
                    value = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, list):
                value = json.dumps(value, ensure_ascii=False)
            # Signature: indiquer seulement qu'elle existe
            if isinstance(value, str) and value.startswith("data:image/"):
                value = "[Signature image]"
            ws.cell(row=row_num, column=col_num).value = str(value)
    
    # Ajuster la largeur des colonnes
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Sauvegarder dans un buffer
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=soumissions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )


async def _export_json(soumission_ids: List[int], db: AsyncSession) -> StreamingResponse:
    """Exporter en JSON"""
    # Récupérer les soumissions
    result = await db.execute(
        select(Soumission).where(Soumission.id.in_(soumission_ids))
    )
    soumissions = result.scalars().all()
    
    if not soumissions:
        raise HTTPException(status_code=404, detail="Aucune soumission trouvée")
    
    # Préparer les données
    data = []
    for soumission in soumissions:
        data.append({
            "id": soumission.id,
            "formulaire_id": soumission.formulaire_id,
            "date_soumission": soumission.date_soumission.isoformat() if soumission.date_soumission else None,
            "statut": soumission.statut,
            "utilisateur_id": soumission.utilisateur_id,
            "donnees": soumission.donnees
        })
    
    # Créer le JSON
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    
    return StreamingResponse(
        iter([json_data]),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=soumissions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        }
    )
