from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.sql import func
from app.db.base import Base


class ConsentementRGPD(Base):
    __tablename__ = "consentement_rgpd"

    id = Column(Integer, primary_key=True, index=True)
    soumission_id = Column(
        Integer, ForeignKey("soumission.id", ondelete="CASCADE"), nullable=False
    )
    type_consentement = Column(String(100), nullable=False)
    accepte = Column(Boolean, nullable=False)
    date_consentement = Column(DateTime, server_default=func.now())
    ip_adresse = Column(INET, nullable=True)


class DemandeSuppression(Base):
    __tablename__ = "demande_suppression"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(
        Integer, ForeignKey("utilisateur.id", ondelete="CASCADE"), nullable=True
    )
    soumission_id = Column(
        Integer, ForeignKey("soumission.id", ondelete="CASCADE"), nullable=True
    )
    raison = Column(Text, nullable=True)
    statut = Column(String(20), default="ACCEPTEE")
    date_demande = Column(DateTime, server_default=func.now())
    date_execution = Column(DateTime, nullable=True)
