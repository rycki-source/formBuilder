"""Service de gestion des rôles et permissions"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.role import Role, Permission, user_role
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate, PermissionCreate
from typing import Optional, List


class RolePermissionService:
    """Service pour gérer les rôles et permissions"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ===== PERMISSIONS =====

    async def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """Créer une nouvelle permission"""
        permission = Permission(**permission_data.model_dump())
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def get_permission(self, permission_id: int) -> Optional[Permission]:
        """Récupérer une permission par ID"""
        result = await self.db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()

    async def get_permission_by_code(self, code: str) -> Optional[Permission]:
        """Récupérer une permission par code"""
        result = await self.db.execute(
            select(Permission).where(Permission.code == code)
        )
        return result.scalar_one_or_none()

    async def list_permissions(
        self,
        categorie: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Permission]:
        """Lister les permissions"""
        query = select(Permission)

        if categorie:
            query = query.where(Permission.categorie == categorie)

        query = query.order_by(Permission.categorie, Permission.nom)
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ===== ROLES =====

    async def create_role(self, role_data: RoleCreate) -> Role:
        """Créer un nouveau rôle"""
        role = Role(
            code=role_data.code,
            nom=role_data.nom,
            description=role_data.description,
            actif=role_data.actif
        )

        # Ajouter les permissions
        if role_data.permission_ids:
            for perm_id in role_data.permission_ids:
                permission = await self.get_permission(perm_id)
                if permission:
                    role.permissions.append(permission)

        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role, ["permissions"])
        return role

    async def get_role(self, role_id: int) -> Optional[Role]:
        """Récupérer un rôle par ID avec ses permissions"""
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        return result.scalar_one_or_none()

    async def get_role_by_code(self, code: str) -> Optional[Role]:
        """Récupérer un rôle par code"""
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.code == code)
        )
        return result.scalar_one_or_none()

    async def list_roles(
        self,
        actif: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Role]:
        """Lister les rôles"""
        query = select(Role).options(selectinload(Role.permissions))

        if actif is not None:
            query = query.where(Role.actif == actif)

        query = query.order_by(Role.nom)
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        """Mettre à jour un rôle"""
        role = await self.get_role(role_id)
        if role is None:
            return None
        
        # Ne pas modifier les rôles système (extraction de la valeur pour éviter Column comparison)
        if getattr(role, 'is_system', False):
            return None

        # Mise à jour des champs simples
        for key, value in role_data.model_dump(exclude_unset=True, exclude={'permission_ids'}).items():
            setattr(role, key, value)

        # Mise à jour des permissions
        if role_data.permission_ids is not None:
            role.permissions.clear()
            for perm_id in role_data.permission_ids:
                permission = await self.get_permission(perm_id)
                if permission:
                    role.permissions.append(permission)

        await self.db.commit()
        await self.db.refresh(role, ["permissions"])
        return role

    async def delete_role(self, role_id: int) -> bool:
        """Supprimer un rôle (si non système)"""
        role = await self.get_role(role_id)
        if role is None:
            return False
        
        # Ne pas supprimer les rôles système (extraction de la valeur pour éviter Column comparison)
        if getattr(role, 'is_system', False):
            return False

        await self.db.delete(role)
        await self.db.commit()
        return True

    # ===== USER ROLES =====

    async def assign_roles_to_user(self, user_id: int, role_ids: List[int]) -> bool:
        """Assigner des rôles à un utilisateur"""
        # Vérifier que l'utilisateur existe
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return False

        # Supprimer les anciens rôles
        await self.db.execute(
            user_role.delete().where(user_role.c.user_id == user_id)
        )

        # Ajouter les nouveaux rôles
        for role_id in role_ids:
            role = await self.get_role(role_id)
            if role:
                await self.db.execute(
                    user_role.insert().values(user_id=user_id, role_id=role_id)
                )

        await self.db.commit()
        return True

    async def get_user_roles(self, user_id: int) -> List[Role]:
        """Obtenir les rôles d'un utilisateur"""
        result = await self.db.execute(
            select(Role)
            .join(user_role)
            .where(user_role.c.user_id == user_id)
            .options(selectinload(Role.permissions))
        )
        return list(result.scalars().all())

    async def get_user_permissions(self, user_id: int) -> List[Permission]:
        """Obtenir toutes les permissions d'un utilisateur (via ses rôles)"""
        roles = await self.get_user_roles(user_id)
        permissions = set()
        for role in roles:
            permissions.update(role.permissions)
        return list(permissions)

    async def user_has_permission(self, user_id: int, permission_code: str) -> bool:
        """Vérifier si un utilisateur a une permission spécifique"""
        permissions = await self.get_user_permissions(user_id)
        return any(p.code == permission_code for p in permissions)
