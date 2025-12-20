"""
Middleware de validation pour les requêtes d'inscription
Validation supplémentaire et gestion d'erreurs améliorée
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
import json
from typing import Dict, Any

from app.utils.validation import FormValidator


class RegistrationValidationMiddleware(BaseHTTPMiddleware):
    """Middleware pour validation stricte des données d'inscription"""
    
    async def dispatch(self, request: Request, call_next):
        """Intercepter et valider les requêtes d'inscription"""
        
        # Vérifier si c'est une requête d'inscription
        if (request.method == "POST" and 
            request.url.path.endswith("/auth/register")):
            
            # Lire le corps de la requête
            body = await request.body()
            
            try:
                data = json.loads(body.decode())
                
                # Validation avec notre validateur personnalisé
                validation_result = FormValidator.validate_registration_data(data)
                
                if not validation_result.is_valid:
                    return JSONResponse(
                        status_code=422,
                        content={
                            "detail": {
                                "error": "VALIDATION_FAILED",
                                "message": "Les données fournies ne respectent pas les règles de validation",
                                "validation_errors": validation_result.errors,
                                "action": "Corrigez les erreurs et réessayez"
                            }
                        }
                    )
                
                # Reconstruire la requête avec les données validées
                request._body = json.dumps(data).encode()
                
            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=400,
                    content={
                        "detail": {
                            "error": "INVALID_JSON",
                            "message": "Format de données invalide",
                            "action": "Vérifiez le format JSON"
                        }
                    }
                )
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={
                        "detail": {
                            "error": "VALIDATION_ERROR",
                            "message": f"Erreur de validation: {str(e)}",
                            "action": "Contactez l'administrateur"
                        }
                    }
                )
        
        # Continuer avec la requête normale
        response = await call_next(request)
        return response


def format_validation_error(exc: ValidationError) -> Dict[str, Any]:
    """Formater les erreurs de validation Pydantic"""
    errors = []
    
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        
        # Messages personnalisés pour les erreurs communes
        if "ensure this value has at least" in message:
            if "characters" in message:
                errors.append(f"{field}: Longueur minimale non respectée")
            else:
                errors.append(f"{field}: Valeur minimale non respectée")
        elif "ensure this value has at most" in message:
            if "characters" in message:
                errors.append(f"{field}: Longueur maximale dépassée")
            else:
                errors.append(f"{field}: Valeur maximale dépassée")
        elif "field required" in message:
            errors.append(f"{field}: Champ obligatoire manquant")
        elif "value is not a valid email address" in message:
            errors.append(f"{field}: Format d'adresse email invalide")
        else:
            # Utiliser le message d'erreur personnalisé si disponible
            errors.append(f"{field}: {message}")
    
    return {
        "error": "VALIDATION_FAILED",
        "message": "Les données fournies ne respectent pas les règles de validation",
        "validation_errors": errors,
        "action": "Corrigez les erreurs et réessayez"
    }


async def validation_exception_handler(request: Request, exc: ValidationError):
    """Gestionnaire d'exception pour les erreurs de validation Pydantic"""
    return JSONResponse(
        status_code=422,
        content={"detail": format_validation_error(exc)}
    )


async def value_error_handler(request: Request, exc: ValueError):
    """Gestionnaire d'exception pour les erreurs de validation personnalisées"""
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "error": "VALIDATION_FAILED", 
                "message": str(exc),
                "action": "Vérifiez vos données et réessayez"
            }
        }
    )