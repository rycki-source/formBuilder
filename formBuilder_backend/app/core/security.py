from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configuration bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _get_settings():
    """Lazy import to avoid circular dependency"""
    from app.core.config import settings
    return settings


def hash_password(password: str) -> str:
    """Hash password avec bcrypt + pepper"""
    salted_password = f"{password}{_get_settings().PEPPER}"
    return pwd_context.hash(salted_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier le mot de passe"""
    salted_password = f"{plain_password}{_get_settings().PEPPER}"
    return pwd_context.verify(salted_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Créer un token JWT"""
    to_encode = data.copy()
    settings = _get_settings()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Décoder et valider un token JWT"""
    try:
        settings = _get_settings()
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def create_refresh_token(user_id: int) -> str:
    """Créer un refresh token"""
    expires_delta = timedelta(days=7)
    return create_access_token(
        data={"sub": str(user_id), "type": "refresh"}, expires_delta=expires_delta
    )
