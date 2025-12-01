from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from app.models.soumission import Soumission
from app.schemas.soumission import SoumissionCreate, SoumissionResponse
from app.services.validation_service import ValidationService
from app.services.audit_service import AuditService
from app.api.dependencies import get_current_user
from sqlalchemy import select
from typing import List

router = APIRouter(prefix="/soumissions", tags=["soumissions"])

@router.post("/", response_model=SoumissionResponse, status_code=201)
async def create_soumission(
    request: Request,
    soumission_data: SoumissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soumettre un formulaire"""
    # Récupérer le formulaire
    from app.services.formulaire_service import FormulaireService
    form_service = FormulaireService(db)
    formulaire = await form_service.get_formulaire(soumission_data.formulaire_id)

    if not formulaire:
        raise HTTPException(status_code=404, detail="Formulaire non trouvé")

    # Valider la soumission
    valide, erreurs = ValidationService.validate_soumission(
        soumission_data.donnees,
        formulaire.structure_json
    )

    if not valide:
        raise HTTPException(status_code=422, detail={"erreurs": erreurs})

    # Créer la soumission
    new_soumission = Soumission(
        formulaire_id=soumission_data.formulaire_id,
        donnees=soumission_data.donnees,
        utilisateur_id=current_user.id,
        version_formulaire=formulaire.version,
        statut="SOUMIS"
    )
    db.add(new_soumission)
    await db.commit()
    await db.refresh(new_soumission)

    # Log audit
    audit_service = AuditService(db)
    await audit_service.log_action(
        action="SOUMISSION_CREEE",
        module="SOUMISSION",
        utilisateur_id=current_user.id,
        ressource_type="soumission",
        ressource_id=new_soumission.id,
        ip_adresse=request.client.host
    )

    return new_soumission

@router.get("/", response_model=List[SoumissionResponse])
async def list_soumissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les soumissions de l'utilisateur"""
    result = await db.execute(
        select(Soumission).where(Soumission.utilisateur_id == current_user.id)
    )
    soumissions = result.scalars().all()
    return soumissions

@router.get("/{soumission_id}", response_model=SoumissionResponse)
async def get_soumission(
    soumission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Récupérer une soumission"""
    result = await db.execute(
        select(Soumission).where(Soumission.id == soumission_id)
    )
    soumission = result.scalar_one_or_none()

    if not soumission:
        raise HTTPException(status_code=404, detail="Soumission non trouvée")

    return soumission