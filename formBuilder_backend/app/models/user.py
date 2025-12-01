from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    DEVELOPPEUR = "DEVELOPPEUR"
    UTILISATEUR = "UTILISATEUR"


class UserStatusEnum(str, enum.Enum):
    ACTIF = "ACTIF"
    INACTIF = "INACTIF"
    BLOQUE = "BLOQUE"


class User(Base):
    __tablename__ = "utilisateur"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    mot_de_passe = Column(String(255), nullable=False)
    role = Column(String(50), default=RoleEnum.UTILISATEUR)
    statut = Column(String(20), default=UserStatusEnum.ACTIF)
    date_creation = Column(DateTime, server_default=func.now())
    derniere_connexion = Column(DateTime, nullable=True)
    modifier_profil = Column(Boolean, default=True)
    verifier_permission = Column(Boolean, default=True)
    actif = Column(Boolean, default=True, index=True)
