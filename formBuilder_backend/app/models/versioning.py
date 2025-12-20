"""
Modèles pour le versioning et l'historique des formulaires
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class FormulaireVersion(Base):
    """Versions des formulaires pour historique et rollback"""
    __tablename__ = "formulaire_versions"

    id = Column(Integer, primary_key=True, index=True)
    formulaire_id = Column(Integer, ForeignKey("formulaire.id", ondelete="CASCADE"), nullable=False)
    
    # Numéro de version
    version_number = Column(Integer, nullable=False)
    version_tag = Column(String(50), nullable=True)  # Ex: "v1.0", "draft", "production"
    
    # Snapshot complet du formulaire
    nom = Column(String(255))
    description = Column(Text, nullable=True)
    structure_json = Column(JSON)
    type_structurel = Column(String(50))
    type_fonctionnel = Column(String(50))
    
    # Métadonnées
    created_by = Column(Integer, ForeignKey("utilisateur.id"))
    created_at = Column(DateTime, server_default=func.now())
    
    # Commentaire de version
    change_summary = Column(Text, nullable=True)
    
    # Relations
    formulaire = relationship("Formulaire", back_populates="versions")
    created_by_user = relationship("User", foreign_keys=[created_by])


class AuditLog(Base):
    """Log d'audit pour traçabilité complète"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Entité concernée
    entity_type = Column(String(50), nullable=False)  # formulaire, soumission, user, etc.
    entity_id = Column(Integer, nullable=False)
    
    # Action
    action = Column(String(50), nullable=False)  # create, update, delete, publish, etc.
    
    # Utilisateur
    user_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=True)
    username = Column(String(255), nullable=True)
    
    # Détails
    changes = Column(JSON, nullable=True)  # Avant/après pour les updates
    audit_metadata = Column(JSON, nullable=True)  # Infos supplémentaires
    
    # Contexte technique
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # Timestamp
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    
    # Relations
    user = relationship("User", foreign_keys=[user_id])
