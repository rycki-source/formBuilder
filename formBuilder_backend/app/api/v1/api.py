"""Router principal v1"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, formulaires, soumissions, referentiels, exports, users, dashboard
)
# Endpoints admin - import séparé pour éviter les erreurs si modules manquants
try:
    from app.api.v1.endpoints import (
        admin_alerts, admin_db_explorer
    )
    ADMIN_ENDPOINTS_AVAILABLE = True
except ImportError:
    ADMIN_ENDPOINTS_AVAILABLE = False


api_router = APIRouter(prefix="/api/v1")

# Endpoints existants
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(formulaires.router)
api_router.include_router(soumissions.router)
api_router.include_router(referentiels.router)
api_router.include_router(exports.router)
api_router.include_router(dashboard.router)

# Endpoints admin (si disponibles)
if ADMIN_ENDPOINTS_AVAILABLE:
    api_router.include_router(admin_alerts.router)
    api_router.include_router(admin_db_explorer.router)
