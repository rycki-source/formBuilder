from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    ForeignKey,
    Text,
    BigInteger,
    Boolean,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.base import Base


class Soumission(Base):
    __tablename__ = "soumission"

    id = Column(Integer, primary_key=True, index=True)
    formulaire_id = Column(
        Integer,
        ForeignKey("formulaire.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    donnees_json = Column("donnees_json", JSONB, nullable=False)
    statut = Column(String(50), default="SOUMIS", index=True)
    utilisateur_id = Column(
        Integer,
        ForeignKey("utilisateur.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    date_soumission = Column(DateTime, default=func.now(), index=True)
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())
    ip_adresse = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    # Alias pour compatibilité avec les schémas
    @property
    def donnees(self):
        return self.donnees_json
    
    @donnees.setter
    def donnees(self, value):
        self.donnees_json = value


class ValidationSoumission(Base):
    __tablename__ = "validation_soumission"

    id = Column(Integer, primary_key=True, index=True)
    soumission_id = Column(
        Integer,
        ForeignKey("soumission.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    regles_appliquees = Column(JSONB, nullable=False)
    erreurs = Column(JSONB, nullable=True)
    avertissements = Column(JSONB, nullable=True)
    valide = Column(Boolean, default=False)
    date_validation = Column(DateTime, server_default=func.now())


class RapportValidation(Base):
    __tablename__ = "rapport_validation"

    id = Column(Integer, primary_key=True, index=True)
    soumission_id = Column(
        Integer, ForeignKey("soumission.id", ondelete="CASCADE"), nullable=False
    )
    erreurs = Column(JSONB, nullable=True)
    avertissements = Column(JSONB, nullable=True)
    resume_texte = Column(Text, nullable=True)
    date_generation = Column(DateTime, server_default=func.now())


class FichierJoint(Base):
    __tablename__ = "fichier_joint"

    id = Column(Integer, primary_key=True, index=True)
    soumission_id = Column(
        Integer,
        ForeignKey("soumission.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nom_original = Column(String(255), nullable=False)
    nom_stockage = Column(String(255), nullable=False)
    format = Column(String(50), nullable=False)
    chemin_s3 = Column(Text, nullable=False)
    taille_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=True)
    date_upload = Column(DateTime, server_default=func.now())
