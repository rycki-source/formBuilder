"""Modèle Permission pour la gestion des droits d'accès"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

# Table d'association many-to-many entre Role et Permission
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('role.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permission.id', ondelete='CASCADE'), primary_key=True)
)

class Permission(Base):
    """Permissions granulaires pour le système"""
    __tablename__ = 'permission'
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)  # ex: "view_db", "manage_users"
    nom = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    categorie = Column(String(50), nullable=True)  # "database", "users", "forms", "system"
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
