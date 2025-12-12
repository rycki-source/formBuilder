"""Modèle pour l'audit des actions administratives"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class AdminAudit(Base):
    """Modèle pour l'audit log des actions administratives"""
    __tablename__ = "admin_audit"

    id = Column(Integer, primary_key=True, index=True)
    
    # Qui
    user_id = Column(Integer, ForeignKey('utilisateur.id', ondelete='SET NULL'), nullable=True)
    username = Column(String(255), nullable=False)  # Sauvegarde du nom au cas où user supprimé
    
    # Quoi
    action = Column(String(100), nullable=False, index=True)  # CREATE_USER, DELETE_FORM, etc.
    resource_type = Column(String(50), nullable=False)  # user, role, form, database, etc.
    resource_id = Column(Integer, nullable=True)
    
    # Détails
    description = Column(Text, nullable=False)
    changes_json = Column(Text, nullable=True)  # Détails des changements en JSON
    
    # Contexte
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    endpoint = Column(String(255), nullable=True)
    
    # Résultat
    success = Column(Integer, default=True)
    error_message = Column(Text, nullable=True)
    
    # Date
    date_action = Column(DateTime(timezone=True), server_default=func.now(), index=True)
