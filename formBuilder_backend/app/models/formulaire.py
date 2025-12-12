from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.base import Base


class Formulaire(Base):
    __tablename__ = "formulaire"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type_structurel = Column(String(50), nullable=False, default='simple', server_default='simple')
    type_fonctionnel = Column(String(50), nullable=False, default='personnalise', server_default='personnalise')
    structure_json = Column(JSONB, nullable=False)
    date_creation = Column(DateTime, default=func.now(), nullable=False)
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    actif = Column(Boolean, default=True, index=True)
    publie = Column(Boolean, default=False, index=True)
    developpeur_id = Column(
        Integer,
        ForeignKey("utilisateur.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    version = Column(String(20), default="1.0")
    
    # Configuration webhook pour intégration externe
    webhook_url = Column(String(500), nullable=True)  # URL de callback externe
    webhook_enabled = Column(Boolean, default=False)  # Activer/désactiver le webhook
    webhook_secret = Column(String(255), nullable=True)  # Secret pour sécuriser le webhook
    webhook_retry_count = Column(Integer, default=3)  # Nombre de tentatives en cas d'échec


class FormulaireVersion(Base):
    __tablename__ = "formulaire_version"

    id = Column(Integer, primary_key=True, index=True)
    formulaire_id = Column(
        Integer, ForeignKey("formulaire.id", ondelete="CASCADE"), nullable=False
    )
    numero_version = Column(String(20), nullable=False)
    majeur = Column(Integer, nullable=False)
    mineur = Column(Integer, nullable=False)
    patch = Column(Integer, nullable=False)
    structure_json = Column(JSONB, nullable=False)
    commentaire = Column(Text, nullable=True)
    date_creation = Column(DateTime, server_default=func.now())
    auteur_id = Column(
        Integer, ForeignKey("utilisateur.id", ondelete="SET NULL"), nullable=True
    )
    actif = Column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("formulaire_id", "numero_version"),)


class Champ(Base):
    __tablename__ = "champ"

    id = Column(Integer, primary_key=True, index=True)
    formulaire_id = Column(
        Integer,
        ForeignKey("formulaire.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nom = Column(String(255), nullable=False)
    label = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    obligatoire = Column(Boolean, default=False)
    valeur_par_defaut = Column(JSONB, nullable=True)
    visible = Column(Boolean, default=True)
    ordre = Column(Integer, nullable=False)
    config_json = Column(JSONB, nullable=True)


class RegleValidation(Base):
    __tablename__ = "regle_validation"

    id = Column(Integer, primary_key=True, index=True)
    champ_id = Column(
        Integer, ForeignKey("champ.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type = Column(String(100), nullable=False)
    expression = Column(Text, nullable=True)
    message_erreur = Column(String(255), nullable=False)
    dependance_champ_id = Column(
        Integer, ForeignKey("champ.id", ondelete="SET NULL"), nullable=True
    )

