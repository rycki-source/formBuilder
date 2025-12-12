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
    try:
        # Récupérer le formulaire
        from app.services.formulaire_service import FormulaireService
        form_service = FormulaireService(db)
        formulaire = await form_service.get_formulaire(soumission_data.formulaire_id)

        if not formulaire:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "FORMULAIRE_INTROUVABLE",
                    "message": f"Le formulaire avec l'ID {soumission_data.formulaire_id} n'existe pas",
                    "action": "Vérifiez que le formulaire est toujours disponible"
                }
            )

        # Valider la soumission
        valide, erreurs = ValidationService.validate_soumission(
            soumission_data.donnees,
            formulaire.structure_json
        )

        if not valide:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "VALIDATION_ECHOUEE",
                    "message": "Les données soumises ne sont pas valides",
                    "erreurs": erreurs,
                    "action": "Corrigez les champs en erreur et réessayez"
                }
            )

        # Créer la soumission
        user_id = getattr(current_user, 'id', None)
        
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "UTILISATEUR_NON_AUTHENTIFIE",
                    "message": "Impossible d'identifier l'utilisateur",
                    "action": "Reconnectez-vous et réessayez"
                }
            )
        
        new_soumission = Soumission(
            formulaire_id=soumission_data.formulaire_id,
            donnees=soumission_data.donnees,
            utilisateur_id=user_id,
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
            utilisateur_id=user_id,
            ressource_type="soumission",
            ressource_id=new_soumission.id,
            ip_adresse=request.client.host
        )

        return new_soumission
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ERREUR_SOUMISSION",
                "message": f"Erreur lors de la soumission: {str(e)}",
                "action": "Réessayez ou contactez l'administrateur si le problème persiste"
            }
        )

@router.get("/", response_model=List[SoumissionResponse])
async def list_soumissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les soumissions de l'utilisateur"""
    user_id = getattr(current_user, 'id', None)
    result = await db.execute(
        select(Soumission).where(Soumission.utilisateur_id == user_id)
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


@router.put("/{soumission_id}/statut", response_model=SoumissionResponse)
async def update_soumission_status(
    soumission_id: int,
    statut_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mettre à jour le statut d'une soumission"""
    result = await db.execute(
        select(Soumission).where(Soumission.id == soumission_id)
    )
    soumission = result.scalar_one_or_none()

    if not soumission:
        raise HTTPException(status_code=404, detail="Soumission non trouvée")

    # Valider le statut
    statut = statut_data.get("statut")
    if statut not in ["en_attente", "validee", "rejetee"]:
        raise HTTPException(status_code=400, detail="Statut invalide")

    # Mettre à jour le statut
    soumission.statut = statut.upper()
    await db.commit()
    await db.refresh(soumission)

    # Log audit
    user_id = getattr(current_user, 'id', None)
    audit_service = AuditService(db)
    await audit_service.log_action(
        action="SOUMISSION_STATUT_MODIFIE",
        module="SOUMISSION",
        utilisateur_id=user_id,
        ressource_type="soumission",
        ressource_id=soumission.id,
        ip_adresse=request.client.host,
        details={"ancien_statut": soumission.statut, "nouveau_statut": statut}
    )

    return soumission


@router.delete("/{soumission_id}", status_code=204)
async def delete_soumission(
    soumission_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Supprimer une soumission"""
    result = await db.execute(
        select(Soumission).where(Soumission.id == soumission_id)
    )
    soumission = result.scalar_one_or_none()

    if not soumission:
        raise HTTPException(status_code=404, detail="Soumission non trouvée")

    # Log audit avant suppression
    user_id = getattr(current_user, 'id', None)
    audit_service = AuditService(db)
    await audit_service.log_action(
        action="SOUMISSION_SUPPRIMEE",
        module="SOUMISSION",
        utilisateur_id=user_id,
        ressource_type="soumission",
        ressource_id=soumission.id,
        ip_adresse=request.client.host,
        details={"formulaire_id": soumission.formulaire_id}
    )

    await db.delete(soumission)
    await db.commit()

    return None