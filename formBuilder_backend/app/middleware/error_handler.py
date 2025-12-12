"""Gestionnaire d'erreurs centralisé"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError
from pydantic import ValidationError
import traceback
import logging

logger = logging.getLogger(__name__)


def format_error_response(error_type: str, message: str, action: str, status_code: int = 500, extra_data: dict = None):
    """Formater une réponse d'erreur standardisée"""
    response = {
        "error": error_type,
        "message": message,
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": status_code
    }
    
    if extra_data:
        response.update(extra_data)
    
    return response


async def global_exception_handler(request: Request, exc: Exception):
    """Handler global pour les exceptions avec messages détaillés"""
    
    # Log l'erreur
    logger.error(f"Exception globale: {type(exc).__name__} - {str(exc)}", exc_info=True)
    
    # HTTPException de FastAPI (déjà gérée avec nos détails)
    if isinstance(exc, HTTPException):
        # Si le détail est déjà un dict avec notre format, le retourner tel quel
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.detail
            )
        # Sinon, formater avec notre standard
        return JSONResponse(
            status_code=exc.status_code,
            content=format_error_response(
                error_type="HTTP_ERROR",
                message=str(exc.detail),
                action="Vérifiez votre requête et réessayez",
                status_code=exc.status_code
            )
        )
    
    # Erreurs de validation Pydantic
    if isinstance(exc, ValidationError):
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            errors.append(f"{field}: {error['msg']}")
        
        return JSONResponse(
            status_code=422,
            content=format_error_response(
                error_type="VALIDATION_ERROR",
                message="Données invalides",
                action="Corrigez les champs suivants: " + ", ".join(errors),
                status_code=422,
                extra_data={"validation_errors": errors}
            )
        )
    
    # Erreurs de base de données - IntegrityError (contraintes, doublons)
    if isinstance(exc, IntegrityError):
        error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        
        if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
            return JSONResponse(
                status_code=409,
                content=format_error_response(
                    error_type="DUPLICATE_ENTRY",
                    message="Cette entrée existe déjà dans la base de données",
                    action="Utilisez un nom ou identifiant différent",
                    status_code=409
                )
            )
        
        if "foreign key" in error_msg.lower():
            return JSONResponse(
                status_code=400,
                content=format_error_response(
                    error_type="REFERENCE_INVALIDE",
                    message="Référence à un élément inexistant",
                    action="Vérifiez que tous les éléments référencés existent",
                    status_code=400
                )
            )
        
        return JSONResponse(
            status_code=400,
            content=format_error_response(
                error_type="DATABASE_CONSTRAINT",
                message="Violation de contrainte de base de données",
                action="Vérifiez que toutes les données respectent les règles métier",
                status_code=400
            )
        )
    
    # Erreurs de connexion base de données
    if isinstance(exc, OperationalError):
        return JSONResponse(
            status_code=503,
            content=format_error_response(
                error_type="DATABASE_UNAVAILABLE",
                message="La base de données est temporairement indisponible",
                action="Réessayez dans quelques instants. Si le problème persiste, contactez l'administrateur",
                status_code=503
            )
        )
    
    # Autres erreurs de base de données
    if isinstance(exc, DatabaseError):
        return JSONResponse(
            status_code=500,
            content=format_error_response(
                error_type="DATABASE_ERROR",
                message="Erreur lors de l'accès à la base de données",
                action="Contactez l'administrateur système",
                status_code=500
            )
        )
    
    # ValueError (erreurs métier)
    if isinstance(exc, ValueError):
        return JSONResponse(
            status_code=400,
            content=format_error_response(
                error_type="INVALID_VALUE",
                message=str(exc),
                action="Vérifiez les valeurs fournies et corrigez-les",
                status_code=400
            )
        )
    
    # KeyError (clé manquante)
    if isinstance(exc, KeyError):
        return JSONResponse(
            status_code=400,
            content=format_error_response(
                error_type="MISSING_FIELD",
                message=f"Champ requis manquant: {str(exc)}",
                action="Vérifiez que tous les champs obligatoires sont renseignés",
                status_code=400
            )
        )
    
    # TypeError
    if isinstance(exc, TypeError):
        return JSONResponse(
            status_code=400,
            content=format_error_response(
                error_type="TYPE_ERROR",
                message="Type de données incorrect",
                action="Vérifiez le format des données envoyées",
                status_code=400
            )
        )
    
    # Erreur générique
    return JSONResponse(
        status_code=500,
        content=format_error_response(
            error_type="INTERNAL_SERVER_ERROR",
            message=f"Une erreur interne s'est produite: {type(exc).__name__}",
            action="Contactez l'administrateur si le problème persiste",
            status_code=500,
            extra_data={
                "exception_type": type(exc).__name__,
                "path": str(request.url)
            }
        )
    )
