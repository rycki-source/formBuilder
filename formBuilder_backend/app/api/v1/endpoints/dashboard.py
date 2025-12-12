"""Endpoints pour le dashboard administrateur"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.formulaire import Formulaire
from app.models.soumission import Soumission
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class DashboardStats(BaseModel):
    total_formulaires: int
    formulaires_publies: int
    formulaires_supprimes: int
    total_soumissions: int
    soumissions_validees: int
    soumissions_en_attente: int
    soumissions_rejetees: int
    formulaires_recents: List[Dict[str, Any]]


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtenir les statistiques du dashboard"""
    
    user_id = getattr(current_user, 'id', None)
    user_role = getattr(current_user, 'role', None)
    
    # Total formulaires
    if user_role == "ADMIN":
        # Admin voit tous les formulaires actifs
        result = await db.execute(
            select(func.count(Formulaire.id)).where(Formulaire.actif == True)
        )
        total_formulaires = result.scalar() or 0
        
        # Formulaires supprimés (soft delete)
        result = await db.execute(
            select(func.count(Formulaire.id)).where(Formulaire.actif == False)
        )
        formulaires_supprimes = result.scalar() or 0
        
        # Formulaires publiés (actifs uniquement)
        result = await db.execute(
            select(func.count(Formulaire.id)).where(
                Formulaire.actif == True,
                Formulaire.publie == True
            )
        )
        formulaires_publies = result.scalar() or 0
        
        # Total soumissions
        result = await db.execute(select(func.count(Soumission.id)))
        total_soumissions = result.scalar() or 0
        
    else:
        # Utilisateur voit seulement ses formulaires actifs
        result = await db.execute(
            select(func.count(Formulaire.id)).where(
                Formulaire.developpeur_id == user_id,
                Formulaire.actif == True
            )
        )
        total_formulaires = result.scalar() or 0
        
        # Formulaires supprimés de l'utilisateur
        result = await db.execute(
            select(func.count(Formulaire.id)).where(
                Formulaire.developpeur_id == user_id,
                Formulaire.actif == False
            )
        )
        formulaires_supprimes = result.scalar() or 0
        
        # Formulaires publiés de l'utilisateur (actifs uniquement)
        result = await db.execute(
            select(func.count(Formulaire.id)).where(
                Formulaire.developpeur_id == user_id,
                Formulaire.actif == True,
                Formulaire.publie == True
            )
        )
        formulaires_publies = result.scalar() or 0
        
        # Soumissions pour les formulaires de l'utilisateur
        result = await db.execute(
            select(func.count(Soumission.id))
            .join(Formulaire, Soumission.formulaire_id == Formulaire.id)
            .where(Formulaire.developpeur_id == user_id)
        )
        total_soumissions = result.scalar() or 0
    
    # Soumissions par statut (pour tous ou par utilisateur)
    if user_role == "ADMIN":
        # Validées
        result = await db.execute(
            select(func.count(Soumission.id)).where(Soumission.statut == "VALIDEE")
        )
        soumissions_validees = result.scalar() or 0
        
        # En attente
        result = await db.execute(
            select(func.count(Soumission.id)).where(Soumission.statut == "EN_ATTENTE")
        )
        soumissions_en_attente = result.scalar() or 0
        
        # Rejetées
        result = await db.execute(
            select(func.count(Soumission.id)).where(Soumission.statut == "REJETEE")
        )
        soumissions_rejetees = result.scalar() or 0
        
        # Formulaires récents (actifs uniquement)
        result = await db.execute(
            select(Formulaire)
            .where(Formulaire.actif == True)
            .order_by(Formulaire.date_creation.desc())
            .limit(5)
        )
        formulaires_recents_objs = result.scalars().all()
        
    else:
        # Validées pour l'utilisateur
        result = await db.execute(
            select(func.count(Soumission.id))
            .join(Formulaire, Soumission.formulaire_id == Formulaire.id)
            .where(
                Formulaire.developpeur_id == user_id,
                Soumission.statut == "VALIDEE"
            )
        )
        soumissions_validees = result.scalar() or 0
        
        # En attente
        result = await db.execute(
            select(func.count(Soumission.id))
            .join(Formulaire, Soumission.formulaire_id == Formulaire.id)
            .where(
                Formulaire.developpeur_id == user_id,
                Soumission.statut == "EN_ATTENTE"
            )
        )
        soumissions_en_attente = result.scalar() or 0
        
        # Rejetées
        result = await db.execute(
            select(func.count(Soumission.id))
            .join(Formulaire, Soumission.formulaire_id == Formulaire.id)
            .where(
                Formulaire.developpeur_id == user_id,
                Soumission.statut == "REJETEE"
            )
        )
        soumissions_rejetees = result.scalar() or 0
        
        # Formulaires récents de l'utilisateur (actifs uniquement)
        result = await db.execute(
            select(Formulaire)
            .where(
                Formulaire.developpeur_id == user_id,
                Formulaire.actif == True
            )
            .order_by(Formulaire.date_creation.desc())
            .limit(5)
        )
        formulaires_recents_objs = result.scalars().all()
    
    # Formatter les formulaires récents
    formulaires_recents = [
        {
            "id": f.id,
            "nom": f.nom,
            "description": f.description,
            "est_publie": f.publie,
            "date_creation": f.date_creation.isoformat() if hasattr(f, 'date_creation') and f.date_creation is not None else None,
        }
        for f in formulaires_recents_objs
    ]
    
    return DashboardStats(
        total_formulaires=total_formulaires,
        formulaires_publies=formulaires_publies,
        formulaires_supprimes=formulaires_supprimes,
        total_soumissions=total_soumissions,
        soumissions_validees=soumissions_validees,
        soumissions_en_attente=soumissions_en_attente,
        soumissions_rejetees=soumissions_rejetees,
        formulaires_recents=formulaires_recents,
    )
