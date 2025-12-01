from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

# Déterminer le chemin du fichier .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    # Application
    APP_TITLE: str = "FormBuilder API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://fb_user:fb_password@localhost:5432/formbuilder"

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    PEPPER: str = os.getenv("PEPPER", "pepper-change-this")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # CORS
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", '["http://localhost:3000","http://localhost:5173","http://localhost:5174","http://localhost:8000"]')
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string to list"""
        import json
        if isinstance(self.ALLOWED_ORIGINS, str):
            return json.loads(self.ALLOWED_ORIGINS)
        return self.ALLOWED_ORIGINS

    # File Storage
    MINIO_URL: str = os.getenv("MINIO_URL", "http://minio:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minio")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minio123")
    UPLOAD_MAX_SIZE: int = 10485760  # 10MB

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_AUTH: str = "100/minute"
    RATE_LIMIT_SUBMISSION: str = "500/minute"

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        case_sensitive = True


settings = Settings()
