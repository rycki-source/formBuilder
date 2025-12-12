from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Créer un nouveau compte utilisateur"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.register(user_data)
        return user
    except ValueError as e:
        error_msg = str(e)
        if "existe déjà" in error_msg.lower():
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "UTILISATEUR_EXISTANT",
                    "message": "Un compte avec cet email existe déjà",
                    "action": "Utilisez un autre email ou connectez-vous"
                }
            )
        elif "email" in error_msg.lower() and "invalide" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "EMAIL_INVALIDE",
                    "message": "L'adresse email fournie n'est pas valide",
                    "action": "Vérifiez le format de l'email"
                }
            )
        elif "mot de passe" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "MOT_DE_PASSE_FAIBLE",
                    "message": error_msg,
                    "action": "Utilisez un mot de passe plus fort (min. 8 caractères)"
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INSCRIPTION_ECHOUEE",
                    "message": error_msg,
                    "action": "Vérifiez les informations saisies"
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ERREUR_INSCRIPTION",
                "message": f"Erreur lors de l'inscription: {str(e)}",
                "action": "Réessayez ou contactez l'administrateur"
            }
        )

@router.post("/login", response_model=TokenResponse)
async def login(request: Request, credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authentifier un utilisateur"""
    try:
        auth_service = AuthService(db)
        ip_address = request.client.host if request.client else None
        result = await auth_service.login(credentials, ip_address=ip_address)
        return {
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": "bearer"
        }
    except ValueError as e:
        error_msg = str(e)
        if "mot de passe" in error_msg.lower() or "identifiants" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "IDENTIFIANTS_INCORRECTS",
                    "message": "Email ou mot de passe incorrect",
                    "action": "Vérifiez vos identifiants ou réinitialisez votre mot de passe"
                }
            )
        elif "compte" in error_msg.lower() and ("inactif" in error_msg.lower() or "désactivé" in error_msg.lower()):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "COMPTE_INACTIF",
                    "message": "Votre compte a été désactivé",
                    "action": "Contactez l'administrateur pour réactiver votre compte"
                }
            )
        else:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "CONNEXION_ECHOUEE",
                    "message": error_msg,
                    "action": "Vérifiez vos identifiants"
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ERREUR_CONNEXION",
                "message": f"Erreur lors de la connexion: {str(e)}",
                "action": "Réessayez dans quelques instants"
            }
        )

@router.get("/me", response_model=UserResponse)
async def get_current(current_user: User = Depends(get_current_user)):
    """Récupérer l'utilisateur actuel"""
    return current_user