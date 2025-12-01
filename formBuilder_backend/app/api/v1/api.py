"""Router principal v1"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, formulaires, soumissions, referentiels, exports, users


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(formulaires.router)
api_router.include_router(soumissions.router)
api_router.include_router(referentiels.router)
api_router.include_router(exports.router)
