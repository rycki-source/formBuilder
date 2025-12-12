"""Application FastAPI principale"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.middleware.logging import setup_logging
from app.middleware.error_handler import global_exception_handler
import logging

# Setup logging
logger = setup_logging()


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

# CORS middleware - Configuration pour API publique
# En production, restreindre aux domaines autorisés dans settings.allowed_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # Pour les téléchargements de fichiers
)

# Register global exception handler
from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

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
