"""Modèle pour les alertes système"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class AlertStatus(str, enum.Enum):
    """Statuts des alertes"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class AlertType(str, enum.Enum):
    """Types d'alertes"""
    SYSTEM = "system"
    USER = "user"
    FORM = "form"
    SUBMISSION = "submission"
    DATABASE = "database"
    SECURITY = "security"


class Alert(Base):
    """Modèle pour les alertes système"""
    __tablename__ = "alert"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(SQLEnum(AlertStatus), nullable=False, default=AlertStatus.INFO)
    type = Column(SQLEnum(AlertType), nullable=False, default=AlertType.SYSTEM)
    
    # Métadonnées
    metadata_json = Column(Text)  # JSON avec infos supplémentaires
    source = Column(String(100))  # Source de l'alerte (endpoint, module, etc.)
    user_id = Column(Integer, nullable=True)  # Utilisateur concerné
    
    # État
    lu = Column(Boolean, default=False)
    persistent = Column(Boolean, default=True)  # False = toast temporaire
    archive = Column(Boolean, default=False)
    
    # Dates
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_lecture = Column(DateTime(timezone=True), nullable=True)
    date_expiration = Column(DateTime(timezone=True), nullable=True)
