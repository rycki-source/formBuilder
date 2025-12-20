"""Schémas pour les utilisateurs"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.utils.validation import (
    validate_password_strength,
    validate_username_format, 
    validate_name_format,
    FieldValidator
)


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nom d'utilisateur unique")
    email: EmailStr = Field(..., max_length=320, description="Adresse email valide")
    nom: str = Field(..., min_length=2, max_length=100, description="Nom de famille")
    prenom: str = Field(..., min_length=2, max_length=100, description="Prénom")
    role: str = "UTILISATEUR"
    
    @validator('username')
    def validate_username(cls, v):
        return validate_username_format(v)
    
    @validator('nom')
    def validate_nom(cls, v):
        return validate_name_format(v)
    
    @validator('prenom')
    def validate_prenom(cls, v):
        return validate_name_format(v)
    
    @validator('email')
    def validate_email_format(cls, v):
        result = FieldValidator.validate_email(str(v))
        if not result.is_valid:
            raise ValueError("; ".join(result.errors))
        return v


class UserCreate(UserBase):
    mot_de_passe: str = Field(
        ..., 
        min_length=8, 
        max_length=128,
        description="Mot de passe sécurisé (8-128 caractères, majuscule, minuscule, chiffre, caractère spécial)"
    )
    
    @validator('mot_de_passe')
    def validate_password(cls, v):
        return validate_password_strength(v)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, max_length=320, description="Nouvelle adresse email")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Nouveau nom d'utilisateur")
    nom: Optional[str] = Field(None, min_length=2, max_length=100, description="Nouveau nom de famille")
    prenom: Optional[str] = Field(None, min_length=2, max_length=100, description="Nouveau prénom")
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            return validate_username_format(v)
        return v
    
    @validator('nom')
    def validate_nom(cls, v):
        if v is not None:
            return validate_name_format(v)
        return v
    
    @validator('prenom')
    def validate_prenom(cls, v):
        if v is not None:
            return validate_name_format(v)
        return v
    
    @validator('email')
    def validate_email_format(cls, v):
        if v is not None:
            result = FieldValidator.validate_email(str(v))
            if not result.is_valid:
                raise ValueError("; ".join(result.errors))
        return v


class UserAdminUpdate(BaseModel):
    """Modification complète par l'admin (email, username, nom, prenom, role, mot_de_passe optionnel)"""
    email: Optional[EmailStr] = Field(None, max_length=320, description="Nouvelle adresse email")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Nouveau nom d'utilisateur")
    nom: Optional[str] = Field(None, min_length=2, max_length=100, description="Nouveau nom de famille")
    prenom: Optional[str] = Field(None, min_length=2, max_length=100, description="Nouveau prénom")
    role: Optional[str] = Field(None, description="Nouveau rôle")
    mot_de_passe: Optional[str] = Field(None, min_length=8, max_length=128, description="Nouveau mot de passe (optionnel)")
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            return validate_username_format(v)
        return v
    
    @validator('nom')
    def validate_nom(cls, v):
        if v is not None:
            return validate_name_format(v)
        return v
    
    @validator('prenom')
    def validate_prenom(cls, v):
        if v is not None:
            return validate_name_format(v)
        return v
    
    @validator('email')
    def validate_email_format(cls, v):
        if v is not None:
            result = FieldValidator.validate_email(str(v))
            if not result.is_valid:
                raise ValueError("; ".join(result.errors))
        return v
    
    @validator('mot_de_passe')
    def validate_password(cls, v):
        if v is not None and v.strip():
            return validate_password_strength(v)
        return v


class UserResponse(UserBase):
    id: int
    statut: str
    date_creation: datetime
    derniere_connexion: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    mot_de_passe: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
