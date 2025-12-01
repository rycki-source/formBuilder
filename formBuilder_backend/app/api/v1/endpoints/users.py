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
    if str(current_user.role) != "ADMIN":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Créer un nouvel utilisateur (Admin seulement)"""
    if str(current_user.role) != "ADMIN":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Vérifier si l'email existe déjà
    result = await db.execute(select(User).filter(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    
    # Vérifier si le username existe déjà
    result = await db.execute(select(User).filter(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà utilisé")
    
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
@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mettre à jour le rôle d'un utilisateur (Admin seulement)"""
    if str(current_user.role) != "ADMIN":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
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
    if str(current_user.role) != "ADMIN":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
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
    if str(current_user.role) != "ADMIN":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte")
    
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    await db.delete(user)
    await db.commit()
    return None
