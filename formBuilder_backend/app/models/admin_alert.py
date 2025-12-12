"""Modèle Alert pour le système d'alertes administratives"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import enum

class AlertStatus(str, enum.Enum):
    """Statuts possibles pour les alertes"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

class AlertType(str, enum.Enum):
    """Types d'alertes"""
    SYSTEM = "system"
    FORM = "form"
    USER = "user"
    DATABASE = "database"
    SECURITY = "security"

class Alert(Base):
    """Alertes et messages pour le dashboard admin"""
    __tablename__ = 'admin_alert'
    
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    statut = Column(SQLEnum(AlertStatus), nullable=False, default=AlertStatus.INFO)
    type_alert = Column(SQLEnum(AlertType), nullable=False, default=AlertType.SYSTEM)
    
    # Métadonnées
    lu = Column(Boolean, default=False)
    persistant = Column(Boolean, default=True)  # True = historique, False = toast temporaire
    utilisateur_id = Column(Integer, nullable=True)  # Si alert spécifique à un user
    formulaire_id = Column(Integer, nullable=True)  # Si liée à un formulaire
    
    # Données additionnelles
    metadata_json = Column(Text, nullable=True)  # JSON avec infos supplémentaires
    
    # Timestamps
    date_creation = Column(DateTime, default=datetime.utcnow, index=True)
    date_lecture = Column(DateTime, nullable=True)
    date_expiration = Column(DateTime, nullable=True)
