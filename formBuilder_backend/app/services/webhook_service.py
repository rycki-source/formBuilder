"""Service de gestion des webhooks pour les soumissions de formulaires"""

import httpx
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class WebhookService:
    """Service pour envoyer les soumissions vers des URLs externes"""
    
    @staticmethod
    def generate_signature(payload: str, secret: str) -> str:
        """
        Générer une signature HMAC-SHA256 pour sécuriser le webhook
        
        Args:
            payload: Données JSON en string
            secret: Clé secrète du webhook
            
        Returns:
            Signature hexadécimale
        """
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    async def send_webhook(
        url: str,
        data: Dict[str, Any],
        secret: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Envoyer une notification webhook vers une URL externe
        
        Args:
            url: URL de destination du webhook
            data: Données à envoyer
            secret: Clé secrète pour la signature (optionnel)
            max_retries: Nombre maximum de tentatives
            
        Returns:
            Dict avec le résultat de l'envoi
        """
        # Préparer le payload
        payload_data = {
            "event": "form_submission",
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        payload_json = json.dumps(payload_data, ensure_ascii=False)
        
        # Préparer les headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "FormBuilder-Webhook/1.0",
            "X-FormBuilder-Event": "form_submission"
        }
        
        # Ajouter la signature si un secret est fourni
        if secret:
            signature = WebhookService.generate_signature(payload_json, secret)
            headers["X-FormBuilder-Signature"] = f"sha256={signature}"
        
        # Tentatives d'envoi avec retry
        last_error = None
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        url,
                        content=payload_json,
                        headers=headers
                    )
                    
                    # Vérifier le statut de la réponse
                    if response.status_code in [200, 201, 202, 204]:
                        logger.info(
                            f"Webhook envoyé avec succès à {url} "
                            f"(tentative {attempt + 1}/{max_retries})"
                        )
                        return {
                            "success": True,
                            "status_code": response.status_code,
                            "attempt": attempt + 1,
                            "response": response.text[:500]  # Limiter la taille
                        }
                    else:
                        logger.warning(
                            f"Webhook retourné avec code {response.status_code} "
                            f"(tentative {attempt + 1}/{max_retries})"
                        )
                        last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                        
            except httpx.TimeoutException as e:
                logger.error(f"Timeout lors de l'envoi du webhook à {url}: {str(e)}")
                last_error = f"Timeout: {str(e)}"
                
            except httpx.RequestError as e:
                logger.error(f"Erreur réseau lors de l'envoi du webhook à {url}: {str(e)}")
                last_error = f"Erreur réseau: {str(e)}"
                
            except Exception as e:
                logger.error(f"Erreur inattendue lors de l'envoi du webhook: {str(e)}")
                last_error = f"Erreur: {str(e)}"
            
            # Attendre avant de réessayer (sauf pour la dernière tentative)
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep(2 ** attempt)  # Backoff exponentiel: 1s, 2s, 4s...
        
        # Toutes les tentatives ont échoué
        logger.error(
            f"Échec de l'envoi du webhook à {url} après {max_retries} tentatives. "
            f"Dernière erreur: {last_error}"
        )
        return {
            "success": False,
            "error": last_error,
            "attempts": max_retries
        }
    
    @staticmethod
    def verify_signature(payload: str, signature: str, secret: str) -> bool:
        """
        Vérifier la signature d'un webhook reçu
        
        Args:
            payload: Données JSON en string
            signature: Signature reçue (format: "sha256=...")
            secret: Clé secrète
            
        Returns:
            True si la signature est valide
        """
        if not signature.startswith("sha256="):
            return False
            
        expected_signature = WebhookService.generate_signature(payload, secret)
        received_signature = signature.replace("sha256=", "")
        
        return hmac.compare_digest(expected_signature, received_signature)
