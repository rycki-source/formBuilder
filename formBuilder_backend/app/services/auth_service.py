from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, LoginRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.services.audit_service import AuditService
from datetime import datetime
from typing import Optional


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    async def register(self, user_data: UserCreate) -> User:
        """Créer un nouvel utilisateur"""
        # Vérifier si l'email existe déjà
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise ValueError("Cet email est déjà utilisé")

        # Créer l'utilisateur
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            mot_de_passe=hash_password(user_data.mot_de_passe),
            role="UTILISATEUR",
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        # Log audit
        await self.audit.log_action(
            action="USER_CREATED",
            module="AUTH",
            details={"user_id": new_user.id, "email": new_user.email},
        )
        return new_user

    async def login(self, credentials: LoginRequest, ip_address: Optional[str] = None) -> dict:
        """Authentifier un utilisateur"""
        result = await self.db.execute(
            select(User).where(User.email == credentials.email)
        )
        
        # Utiliser scalars() pour obtenir directement les instances du modèle
        user = result.scalars().first()

        if not user or not verify_password(credentials.mot_de_passe, getattr(user, "mot_de_passe")):
            await self.audit.log_action(
                action="LOGIN_FAILED",
                module="AUTH",
                details={"email": credentials.email},
                resultat="FAILED",
            )
            raise ValueError("Email ou mot de passe incorrect")

        if getattr(user, "statut", None) != "ACTIF":
            raise ValueError("Compte inactif")

        # Générer tokens
        user_id: int = user.id  # type: ignore
        access_token = create_access_token(data={"sub": str(user_id), "email": user.email})
        refresh_token = create_refresh_token(user_id)

        # Mettre à jour dernière connexion
        setattr(user, "derniere_connexion", datetime.utcnow())
        await self.db.commit()

        # Log audit
        await self.audit.log_action(
            action="LOGIN_SUCCESS",
            module="AUTH",
            utilisateur_id=getattr(user, "id"),
            ip_adresse=ip_address,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user,
        }
