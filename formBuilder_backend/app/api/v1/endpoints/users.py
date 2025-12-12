from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.db.session import get_db
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.models.user import User
from app.api.dependencies import get_current_user
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])
@router.get("", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lister tous les utilisateurs (Admin seulement)"""
    if getattr(current_user, 'role', None) != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "ACCES_NON_AUTORISE",
                "message": "Vous n'avez pas les droits d'administration",
                "action": "Contactez un administrateur pour obtenir les autorisations"
            }
        )
    
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ERREUR_LISTE_UTILISATEURS",
                "message": f"Erreur lors de la récupération des utilisateurs: {str(e)}",
                "action": "Réessayez ou contactez l'administrateur"
            }
        )
@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Créer un nouvel utilisateur (Admin seulement)"""
    if getattr(current_user, 'role', None) != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "ACCES_NON_AUTORISE",
                "message": "Vous n'avez pas les droits d'administration",
                "action": "Contactez un administrateur pour obtenir les autorisations"
            }
        )
    
    try:
        # Vérifier si l'email existe déjà
        result = await db.execute(select(User).filter(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "EMAIL_DEJA_UTILISE",
                    "message": "Cet email est déjà associé à un compte",
                    "action": "Utilisez une autre adresse email"
                }
            )
        
        # Vérifier si le username existe déjà
        result = await db.execute(select(User).filter(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "USERNAME_DEJA_UTILISE",
                    "message": "Ce nom d'utilisateur est déjà pris",
                    "action": "Choisissez un autre nom d'utilisateur"
                }
            )
        
        # Créer l'utilisateur
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            mot_de_passe=hash_password(user_data.mot_de_passe),
            role=getattr(user_data, 'role', 'UTILISATEUR'),
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ERREUR_CREATION_UTILISATEUR",
                "message": f"Erreur lors de la création de l'utilisateur: {str(e)}",
                "action": "Vérifiez les données et réessayez"
            }
        )
@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mettre à jour le rôle d'un utilisateur (Admin seulement)"""
    if getattr(current_user, 'role', None) != "ADMIN":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    role = data.get("role")
    if role is None:
        raise HTTPException(status_code=400, detail="Le rôle est requis")
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user
@router.put("/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mettre à jour le statut d'un utilisateur (Admin seulement)"""
    if getattr(current_user, 'role', None) != "ADMIN":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    statut = data.get("statut")
    if statut is None:
        raise HTTPException(status_code=400, detail="Le statut est requis")
    user.statut = statut
    await db.commit()
    await db.refresh(user)
    return user
@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Supprimer un utilisateur (Admin seulement)"""
    if getattr(current_user, 'role', None) != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "ACCES_NON_AUTORISE",
                "message": "Vous n'avez pas les droits d'administration",
                "action": "Contactez un administrateur pour obtenir les autorisations"
            }
        )
    
    user_id_current = getattr(current_user, 'id', None)
    if user_id == user_id_current:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "SUPPRESSION_INTERDITE",
                "message": "Vous ne pouvez pas supprimer votre propre compte",
                "action": "Demandez à un autre administrateur de supprimer votre compte"
            }
        )
    
    try:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "UTILISATEUR_INTROUVABLE",
                    "message": f"Aucun utilisateur trouvé avec l'ID {user_id}",
                    "action": "Vérifiez l'ID et réessayez"
                }
            )
        
        await db.delete(user)
        await db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ERREUR_SUPPRESSION",
                "message": f"Erreur lors de la suppression: {str(e)}",
                "action": "Réessayez ou contactez l'administrateur"
            }
        )
