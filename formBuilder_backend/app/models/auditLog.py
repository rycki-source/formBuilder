from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.sql import func
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=True)
    action = Column(String(255), nullable=False)
    module = Column(String(100), nullable=True)
    ip = Column(INET, nullable=True)
    details = Column(JSONB, nullable=True)
    date_action = Column(DateTime, server_default=func.now(), index=True)
    resultat = Column(JSONB, nullable=True)
    enregistrer_action = Column(Boolean, default=True)
