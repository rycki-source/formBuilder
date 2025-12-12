"""Modèle pour les logs d'erreurs"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class ErrorSeverity(str, enum.Enum):
    """Niveaux de gravité des erreurs"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorType(str, enum.Enum):
    """Types d'erreurs"""
    VALIDATION = "ValidationError"
    DATABASE = "DatabaseError"
    AUTH = "AuthError"
    PERMISSION = "PermissionError"
    NOT_FOUND = "NotFoundError"
    SERVER = "ServerError"
    NETWORK = "NetworkError"
    TIMEOUT = "TimeoutError"
    UNKNOWN = "UnknownError"


class ErrorLog(Base):
    """Modèle pour les logs d'erreurs"""
    __tablename__ = "error_log"

    id = Column(Integer, primary_key=True, index=True)
    
    # Classification
    type_erreur = Column(SQLEnum(ErrorType), nullable=False)
    severite = Column(SQLEnum(ErrorSeverity), nullable=False, default=ErrorSeverity.MEDIUM)
    
    # Détails
    message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    
    # Contexte
    endpoint = Column(String(255), nullable=True)
    methode_http = Column(String(10), nullable=True)
    user_id = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Métadonnées
    metadata_json = Column(Text)  # Données supplémentaires en JSON
    request_data = Column(Text, nullable=True)  # Données de la requête
    
    # État
    resolu = Column(Integer, default=False)
    notes = Column(Text, nullable=True)
    
    # Dates
    date_erreur = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    date_resolution = Column(DateTime(timezone=True), nullable=True)
