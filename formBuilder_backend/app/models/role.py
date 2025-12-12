"""Modèles pour la gestion des rôles et permissions"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


# Table d'association pour la relation many-to-many entre Role et Permission
role_permission = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('role.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permission.id', ondelete='CASCADE'), primary_key=True)
)


# Table d'association pour la relation many-to-many entre User et Role
user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('utilisateur.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
)


class Permission(Base):
    """Modèle pour les permissions"""
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    nom = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    categorie = Column(String(50), nullable=True)  # users, forms, database, alerts, errors
    
    # Relations
    roles = relationship("Role", secondary=role_permission, back_populates="permissions")
    
    # Dates
    date_creation = Column(DateTime(timezone=True), server_default=func.now())


class Role(Base):
    """Modèle pour les rôles"""
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration
    is_system = Column(Boolean, default=False)  # Rôle système non modifiable
    actif = Column(Boolean, default=True)
    
    # Relations
    permissions = relationship("Permission", secondary=role_permission, back_populates="roles")
    
    # Dates
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
