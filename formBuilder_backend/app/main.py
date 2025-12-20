"""Application FastAPI principale"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import ValidationError
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.middleware.validation import (
    RegistrationValidationMiddleware,
    validation_exception_handler,
    value_error_handler
)
import logging

# Setup logging simple
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("formbuilder")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Créer les tables
    logger.info("Application démarrage...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    logger.info("Application arrêt...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="FormBuilder - Plateforme de génération dynamique de formulaires pour NG-STARs",
    lifespan=lifespan,
)

# CORS middleware - MUST be added BEFORE other middlewares
# Configuration permissive pour développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser toutes les origines en développement
    allow_credentials=True,
    allow_methods=["*"],  # Autoriser toutes les méthodes
    allow_headers=["*"],  # Autoriser tous les headers
    expose_headers=["*"],
)

# Ajout du middleware de validation d'inscription
app.add_middleware(RegistrationValidationMiddleware)

# Register global exception handlers
from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

# Gestionnaires d'exceptions pour validation
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)

@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    # Logger l'erreur complète
    logger.error(f"Exception non gérée: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return await global_exception_handler(request, exc)

# Include routers
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "environment": settings.ENVIRONMENT,
    }
