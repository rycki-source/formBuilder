"""Service pour les soumissions avec validation avancée"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.soumission import Soumission
from app.models.validation_models import ValidationSoumission, RapportValidation
from app.models.formulaire import Formulaire
from app.services.validation_service import ValidationService
from app.services.dynamic_validation_service import DynamicFormValidationService
from app.services.webhook_service import WebhookService
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING
from datetime import datetime
import logging

if TYPE_CHECKING:
    from app.schemas.soumission import SoumissionCreate

logger = logging.getLogger(__name__)


class SoumissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dynamic_validation_service = DynamicFormValidationService(db)

    async def _save_validation_results(self, soumission_id: int, validation_result: Dict[str, Any]):
        """Sauvegarde les résultats de validation en base de données"""
        try:
            # Créer un enregistrement de validation
            validation_record = ValidationSoumission(
                soumission_id=soumission_id,
                est_valide=validation_result["valid"],
                erreurs_validation=validation_result.get("errors", {}),
                avertissements=validation_result.get("warnings", {}),
                score_validation=self._calculate_validation_score(validation_result),
                date_validation=datetime.utcnow()
            )
            
            self.db.add(validation_record)
            
            # Créer un rapport de validation détaillé
            rapport = RapportValidation(
                soumission_id=soumission_id,
                details_validation={
                    "summary": validation_result.get("summary", {}),
                    "field_validations": validation_result.get("field_validations", {}),
                    "suggestions": validation_result.get("suggestions", {}),
                    "timestamp": validation_result.get("timestamp")
                },
                recommandations=self._generate_recommendations(validation_result)
            )
            
            self.db.add(rapport)
            await self.db.commit()
            
            logger.info(f"Résultats de validation sauvegardés pour soumission {soumission_id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des résultats de validation: {str(e)}")
            # Ne pas faire échouer la soumission si la sauvegarde échoue
    
    def _calculate_validation_score(self, validation_result: Dict[str, Any]) -> float:
        """Calcule un score de validation (0-100)"""
        summary = validation_result.get("summary", {})
        total_fields = summary.get("total_fields", 1)
        valid_fields = summary.get("valid_fields", 0)
        
        if total_fields == 0:
            return 100.0
        
        base_score = (valid_fields / total_fields) * 100
        
        # Pénalités pour les warnings
        warning_count = summary.get("warning_count", 0)
        if warning_count > 0:
            penalty = min(warning_count * 2, 20)  # Max 20 points de pénalité
            base_score -= penalty
        
        return max(0.0, min(100.0, base_score))
    
    def _generate_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur les résultats de validation"""
        recommendations = []
        
        summary = validation_result.get("summary", {})
        errors = validation_result.get("errors", {})
        warnings = validation_result.get("warnings", {})
        
        if summary.get("error_count", 0) > 0:
            recommendations.append("Corrigez les erreurs de validation pour améliorer la qualité des données")
        
        if summary.get("warning_count", 0) > 0:
            recommendations.append("Examinez les avertissements pour optimiser la saisie des données")
        
        # Recommandations spécifiques par type d'erreur
        for field, field_errors in errors.items():
            if "mot de passe" in field.lower():
                recommendations.append("Renforcez la politique de mots de passe")
            elif "email" in field.lower():
                recommendations.append("Vérifiez le format des adresses email")
            elif "téléphone" in field.lower() or "phone" in field.lower():
                recommendations.append("Clarifiez le format attendu pour les numéros de téléphone")
        
        return recommendations

    async def create_soumission(
        self,
        soumission_data: 'SoumissionCreate',
        user_id: Optional[int] = None
    ) -> Tuple[Soumission, Dict[str, Any]]:
        """Créer une soumission avec validation avancée et envoyer le webhook si configuré"""
        
        # ÉTAPE 1: Validation avancée des données
        validation_result = await self.dynamic_validation_service.validate_soumission(
            soumission_data.formulaire_id, 
            soumission_data.donnees
        )
        
        # Si la validation échoue, lever une exception avec détails
        if not validation_result["valid"]:
            logger.warning(f"Validation échouée pour formulaire {soumission_data.formulaire_id}: {validation_result['errors']}")
            raise ValueError({
                "error": "VALIDATION_FAILED",
                "message": "Les données du formulaire ne respectent pas les règles de validation",
                "validation_errors": validation_result["errors"],
                "warnings": validation_result.get("warnings", {}),
                "summary": validation_result.get("summary", {}),
                "action": "Corrigez les erreurs et soumettez à nouveau"
            })
        
        # ÉTAPE 2: Créer la soumission si validation réussie
        new_soumission = Soumission(
            formulaire_id=soumission_data.formulaire_id,
            donnees=soumission_data.donnees,
            utilisateur_id=user_id,
            statut="SOUMIS",
        )
        self.db.add(new_soumission)
        await self.db.commit()
        await self.db.refresh(new_soumission)
        
        # ÉTAPE 3: Enregistrer les résultats de validation
        await self._save_validation_results(new_soumission.id, validation_result)
        
        # ÉTAPE 4: Traitement webhook
        # Récupérer le formulaire pour vérifier la configuration webhook
        result = await self.db.execute(
            select(Formulaire).where(Formulaire.id == soumission_data.formulaire_id)
        )
        formulaire = result.scalar_one_or_none()
        
        # Envoyer le webhook si activé
        if formulaire and formulaire.webhook_enabled and formulaire.webhook_url:
            logger.info(f"Envoi du webhook pour la soumission {new_soumission.id}")
            
            webhook_data = {
                "soumission_id": new_soumission.id,
                "formulaire_id": soumission_data.formulaire_id,
                "formulaire_nom": formulaire.nom,
                "donnees": soumission_data.donnees,
                "date_soumission": new_soumission.date_soumission.isoformat() if new_soumission.date_soumission else None,
                "validation_summary": validation_result.get("summary", {}),
                "warnings": validation_result.get("warnings", {})
            }
            
            webhook_service = WebhookService()
            try:
                await webhook_service.send_webhook(
                    formulaire.webhook_url, 
                    webhook_data,
                    secret=formulaire.webhook_secret
                )
                logger.info(f"Webhook envoyé avec succès pour la soumission {new_soumission.id}")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du webhook pour la soumission {new_soumission.id}: {str(e)}")
                # Ne pas faire échouer la soumission si le webhook échoue
        
        return new_soumission, validation_result
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
