"""Gestionnaire d'erreurs centralisé"""

from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
import traceback


async def global_exception_handler(request: Request, exc: Exception):
    """Handler global pour les exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Une erreur serveur s'est produite",
            "error_code": "INTERNAL_SERVER_ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
        },
    )
