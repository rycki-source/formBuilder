"""Service pour les soumissions"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.soumission import Soumission, ValidationSoumission, RapportValidation
from app.models.formulaire import Formulaire
from app.services.validation_service import ValidationService
from app.services.webhook_service import WebhookService
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SoumissionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_soumission(
        self,
        formulaire_id: int,
        donnees: Dict[str, Any],
        utilisateur_id: Optional[int] = None,
        version: str = "1.0",
    ) -> Soumission:
        """Créer une soumission et envoyer le webhook si configuré"""
        new_soumission = Soumission(
            formulaire_id=formulaire_id,
            donnees=donnees,
            utilisateur_id=utilisateur_id,
            statut="SOUMIS",
        )
        self.db.add(new_soumission)
        await self.db.commit()
        await self.db.refresh(new_soumission)
        
        # Récupérer le formulaire pour vérifier la configuration webhook
        result = await self.db.execute(
            select(Formulaire).where(Formulaire.id == formulaire_id)
        )
        formulaire = result.scalar_one_or_none()
        
        # Envoyer le webhook si activé
        if formulaire and formulaire.webhook_enabled and formulaire.webhook_url:
            logger.info(f"Envoi du webhook pour la soumission {new_soumission.id}")
            
            webhook_data = {
                "soumission_id": new_soumission.id,
                "formulaire_id": formulaire_id,
                "formulaire_nom": formulaire.nom,
                "donnees": donnees,
                "date_soumission": new_soumission.date_soumission.isoformat() if new_soumission.date_soumission else None,
                "utilisateur_id": utilisateur_id
            }
            
            try:
                webhook_result = await WebhookService.send_webhook(
                    url=formulaire.webhook_url,
                    data=webhook_data,
                    secret=formulaire.webhook_secret,
                    max_retries=formulaire.webhook_retry_count or 3
                )
                
                if webhook_result.get("success"):
                    logger.info(f"Webhook envoyé avec succès pour la soumission {new_soumission.id}")
                else:
                    logger.error(
                        f"Échec de l'envoi du webhook pour la soumission {new_soumission.id}: "
                        f"{webhook_result.get('error')}"
                    )
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du webhook: {str(e)}")
        
        return new_soumission

    async def get_soumission(self, soumission_id: int) -> Optional[Soumission]:
        """Récupérer une soumission"""
        result = await self.db.execute(
            select(Soumission).where(Soumission.id == soumission_id)
        )
        return result.scalar_one_or_none()

    async def list_soumissions(
        self, formulaire_id: Optional[int] = None, skip: int = 0, limit: int = 10
    ) -> List[Soumission]:
        """Lister les soumissions"""
        query = select(Soumission)
        if formulaire_id:
            query = query.where(Soumission.formulaire_id == formulaire_id)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_soumission_status(
        self, soumission_id: int, statut: str
    ) -> Optional[Soumission]:
        """Mettre à jour le statut d'une soumission"""
        soumission = await self.get_soumission(soumission_id)
        if not soumission:
            return None

        setattr(soumission, "statut", statut)  # type: ignore[assignment]
        await self.db.commit()
        await self.db.refresh(soumission)
        return soumission
