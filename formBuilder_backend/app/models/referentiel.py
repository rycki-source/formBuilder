from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.base import Base


class Referentiel(Base):
    __tablename__ = "referentiel"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0")
    source_type = Column(String(20), nullable=False)  # EXCEL, BDD, API
    metadata_json = Column(JSONB, nullable=True)
    personne_import_id = Column(
        Integer, ForeignKey("utilisateur.id", ondelete="SET NULL"), nullable=True
    )
    date_import = Column(DateTime, server_default=func.now())
    valide = Column(Boolean, default=False)


class ConnexionBddExterne(Base):
    __tablename__ = "connexion_bdd_externe"

    id = Column(Integer, primary_key=True, index=True)
    referentiel_id = Column(
        Integer, ForeignKey("referentiel.id", ondelete="CASCADE"), nullable=False
    )
    nom = Column(String(255), nullable=False)
    type_bdd = Column(String(50), nullable=False)  # PostgreSQL, MySQL, etc.
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    nom_bdd = Column(String(255), nullable=False)
    utilisateur = Column(String(255), nullable=False)
    mot_de_passe = Column(String(255), nullable=False)
    schema_string = Column(String(100), nullable=True)
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime, server_default=func.now())


class ReferentielDonnees(Base):
    __tablename__ = "referentiel_donnees"

    id = Column(Integer, primary_key=True, index=True)
    referentiel_id = Column(
        Integer,
        ForeignKey("referentiel.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cle = Column(String(255), nullable=False)
    valeur = Column(JSONB, nullable=False)
    hierarchie_json = Column(JSONB, nullable=True)
