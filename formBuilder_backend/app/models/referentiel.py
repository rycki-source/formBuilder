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
from sqlalchemy.orm import relationship
from app.db.base import Base


class Referentiel(Base):
    """Référentiel de formulaire dynamique"""
    __tablename__ = "referentiel"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), nullable=True)
    source_type = Column(String(20), nullable=False)
    metadata_json = Column(JSONB, nullable=True)
    valide = Column(Boolean, nullable=True)
    personne_import_id = Column(
        Integer, ForeignKey("utilisateur.id", ondelete="SET NULL"), nullable=True
    )
    date_import = Column(DateTime, server_default=func.now())
    
    def to_dict(self):
        """Convertit le référentiel en dictionnaire compatible frontend"""
        metadata = self.metadata_json or {}
        config = metadata.get('config', {})
        
        return {
            "id": self.id,
            "refId": config.get('id'),
            "version": self.version,
            "metadata": {
                "name": self.nom,
                "description": self.description,
                "createdAt": self.date_import.isoformat() if self.date_import is not None else None,
                "updatedAt": self.date_import.isoformat() if self.date_import is not None else None,
                "tags": metadata.get("tags", [])
            },
            "config": config,
            "customValidators": metadata.get('customValidators'),
            "customComponents": metadata.get('customComponents'),
            "sourceType": self.source_type,
            "sourceFile": metadata.get('source_file'),
            "isActive": True,
            "isTemplate": False,
            "valide": self.valide
        }


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
