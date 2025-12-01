"""Schémas communs"""

from pydantic import BaseModel
from typing import Any, Generic, TypeVar, List, Optional

T = TypeVar("T")


class PaginationResponse(BaseModel, Generic[T]):
    """Réponse paginée générique"""

    data: List[T]
    total: int
    skip: int
    limit: int


class ErrorResponse(BaseModel):
    """Réponse d'erreur"""

    detail: str
    error_code: Optional[str] = None
    timestamp: Optional[str] = None


class SuccessResponse(BaseModel):
    """Réponse de succès"""

    message: str
    data: Optional[Any] = None
