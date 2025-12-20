"""
Modèles pour la gestion des validations et rapports de validation
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Float,
    Index
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class ValidationSoumission(Base):
    """
    Modèle pour stocker les résultats de validation des soumissions
    """
    __tablename__ = "validation_soumission"

    id = Column(Integer, primary_key=True, index=True)
    soumission_id = Column(
        Integer, 
        ForeignKey("soumission.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    est_valide = Column(Boolean, nullable=False, index=True)
    erreurs_validation = Column(JSONB, nullable=True)
    avertissements = Column(JSONB, nullable=True)
    score_validation = Column(Float, nullable=True)
    date_validation = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Métadonnées de validation
    version_validateur = Column(String(50), default="1.0")
    temps_validation_ms = Column(Integer, nullable=True)
    nombre_champs_valides = Column(Integer, nullable=True)
    nombre_champs_total = Column(Integer, nullable=True)
    
    # Relation avec la soumission
    # soumission = relationship("Soumission", back_populates="validation_results")

    __table_args__ = (
        Index('idx_validation_soumission_date', 'date_validation'),
        Index('idx_validation_soumission_score', 'score_validation'),
        Index('idx_validation_soumission_valide_date', 'est_valide', 'date_validation'),
    )


class RapportValidation(Base):
    """
    Modèle pour les rapports détaillés de validation
    """
    __tablename__ = "rapport_validation"

    id = Column(Integer, primary_key=True, index=True)
    soumission_id = Column(
        Integer, 
        ForeignKey("soumission.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    details_validation = Column(JSONB, nullable=False)
    recommandations = Column(ARRAY(String), nullable=True)
    date_creation = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Métriques détaillées
    champs_en_erreur = Column(ARRAY(String), nullable=True)
    champs_avec_avertissement = Column(ARRAY(String), nullable=True)
    suggestions_amelioration = Column(JSONB, nullable=True)
    
    # Informations de contexte
    type_formulaire = Column(String(100), nullable=True)
    version_template = Column(String(50), nullable=True)
    
    # Relation avec la soumission
    # soumission = relationship("Soumission", back_populates="rapports_validation")

    __table_args__ = (
        Index('idx_rapport_validation_date', 'date_creation'),
        Index('idx_rapport_validation_type', 'type_formulaire'),
    )


class RegleValidationPersonnalisee(Base):
    """
    Règles de validation personnalisées par formulaire
    """
    __tablename__ = "regle_validation_personnalisee"

    id = Column(Integer, primary_key=True, index=True)
    formulaire_id = Column(
        Integer, 
        ForeignKey("formulaire.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    nom = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    condition = Column(JSONB, nullable=False)  # Condition de déclenchement
    action = Column(JSONB, nullable=False)     # Action à effectuer
    priorite = Column(Integer, default=100)    # Priorité d'exécution
    active = Column(Boolean, default=True, index=True)
    date_creation = Column(DateTime, default=func.now(), nullable=False)
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Métadonnées
    auteur_id = Column(
        Integer,
        ForeignKey("utilisateur.id", ondelete="SET NULL"),
        nullable=True
    )
    nombre_utilisations = Column(Integer, default=0)
    derniere_utilisation = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_regle_validation_formulaire_actif', 'formulaire_id', 'active'),
        Index('idx_regle_validation_priorite', 'priorite'),
    )


class HistoriqueValidation(Base):
    """
    Historique des validations pour traçabilité
    """
    __tablename__ = "historique_validation"

    id = Column(Integer, primary_key=True, index=True)
    soumission_id = Column(
        Integer, 
        ForeignKey("soumission.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    action = Column(String(100), nullable=False)  # 'validation', 'correction', 're-validation'
    resultat_avant = Column(JSONB, nullable=True)
    resultat_apres = Column(JSONB, nullable=True)
    utilisateur_id = Column(
        Integer,
        ForeignKey("utilisateur.id", ondelete="SET NULL"),
        nullable=True
    )
    date_action = Column(DateTime, default=func.now(), nullable=False, index=True)
    commentaire = Column(Text, nullable=True)
    
    # Métriques de performance
    temps_execution_ms = Column(Integer, nullable=True)
    regles_appliquees = Column(ARRAY(String), nullable=True)

    __table_args__ = (
        Index('idx_historique_validation_date', 'date_action'),
        Index('idx_historique_validation_action', 'action'),
    )