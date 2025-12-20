"""
Modèles pour les analytics et statistiques
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class FormAnalytics(Base):
    """Statistiques agrégées par formulaire"""
    __tablename__ = "form_analytics"

    id = Column(Integer, primary_key=True, index=True)
    formulaire_id = Column(Integer, ForeignKey("formulaire.id", ondelete="CASCADE"), nullable=False)
    
    # Statistiques
    total_views = Column(Integer, default=0)
    total_submissions = Column(Integer, default=0)
    total_completed = Column(Integer, default=0)
    total_abandoned = Column(Integer, default=0)
    
    # Taux
    completion_rate = Column(Float, default=0.0)  # Pourcentage
    average_time_seconds = Column(Float, default=0.0)  # Temps moyen de remplissage
    
    # Données par période
    date = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relations
    formulaire = relationship("Formulaire", back_populates="analytics")


class SubmissionEvent(Base):
    """Événements de soumission pour tracking détaillé"""
    __tablename__ = "submission_events"

    id = Column(Integer, primary_key=True, index=True)
    formulaire_id = Column(Integer, ForeignKey("formulaire.id", ondelete="CASCADE"))
    soumission_id = Column(Integer, ForeignKey("soumission.id", ondelete="SET NULL"), nullable=True)
    
    # Type d'événement
    event_type = Column(String(50))  # view, start, field_complete, validation_error, submit, abandon
    
    # Détails
    field_name = Column(String(255), nullable=True)
    step_number = Column(Integer, nullable=True)
    error_message = Column(String(500), nullable=True)
    
    # Métadonnées
    user_agent = Column(String(500))
    ip_address = Column(String(50))
    session_id = Column(String(255))
    
    # Timing
    timestamp = Column(DateTime, server_default=func.now())
    duration_seconds = Column(Float, nullable=True)


class FieldAnalytics(Base):
    """Statistiques par champ"""
    __tablename__ = "field_analytics"

    id = Column(Integer, primary_key=True, index=True)
    formulaire_id = Column(Integer, ForeignKey("formulaire.id", ondelete="CASCADE"))
    field_name = Column(String(255))
    
    # Statistiques
    total_filled = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)
    average_time_seconds = Column(Float, default=0.0)
    
    # Erreurs communes
    common_errors = Column(JSON, nullable=True)  # Liste des erreurs fréquentes
    
    date = Column(DateTime, server_default=func.now())
