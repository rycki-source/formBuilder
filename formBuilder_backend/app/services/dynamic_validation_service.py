"""
Service de Validation Dynamique pour FormBuilder
Intégration du moteur de validation avec le système de formulaires existant
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.formulaire import Formulaire, Champ
from app.models.soumission import Soumission
from app.utils.advanced_validation import (
    FormValidationEngine, 
    FieldValidationConfig,
    FieldType,
    FormTemplate,
    FormStructureType
)
from app.schemas.soumission import SoumissionCreate
import json
import logging

logger = logging.getLogger(__name__)

class DynamicFormValidationService:
    """Service de validation dynamique pour formulaires FormBuilder"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = FormValidationEngine()
        self.field_type_mapping = self._create_field_type_mapping()
    
    def _create_field_type_mapping(self) -> Dict[str, FieldType]:
        """Mappage des types de champs FormBuilder vers FieldType"""
        return {
            'text': FieldType.TEXT_SHORT,
            'textarea': FieldType.TEXT_LONG,
            'email': FieldType.EMAIL,
            'password': FieldType.PASSWORD,
            'tel': FieldType.PHONE,
            'number': FieldType.NUMBER,
            'date': FieldType.DATE,
            'time': FieldType.TIME,
            'datetime-local': FieldType.DATETIME,
            'url': FieldType.URL,
            'file': FieldType.FILE,
            'select': FieldType.SELECT_SINGLE,
            'checkbox': FieldType.CHECKBOX,
            'radio': FieldType.RADIO,
            'range': FieldType.NUMBER,
            'color': FieldType.TEXT_SHORT,
            'search': FieldType.TEXT_SHORT,
            'hidden': FieldType.TEXT_SHORT,
        }
    
    async def get_form_validation_config(self, formulaire_id: int) -> Dict[str, FieldValidationConfig]:
        """Récupère la configuration de validation pour un formulaire"""
        
        # Récupérer le formulaire et ses champs
        result = await self.db.execute(
            select(Formulaire).where(Formulaire.id == formulaire_id)
        )
        formulaire = result.scalar_one_or_none()
        
        if not formulaire:
            raise ValueError(f"Formulaire {formulaire_id} non trouvé")
        
        # Récupérer les champs du formulaire
        result = await self.db.execute(
            select(Champ)
            .where(Champ.formulaire_id == formulaire_id)
            .order_by(Champ.ordre)
        )
        champs = result.scalars().all()
        
        validation_config = {}
        
        for champ in champs:
            field_config = self._create_field_config_from_champ(champ)
            validation_config[champ.nom] = field_config
        
        return validation_config
    
    def _create_field_config_from_champ(self, champ: Champ) -> FieldValidationConfig:
        """Crée une configuration de validation à partir d'un Champ"""
        
        # Déterminer le type de champ
        field_type = self.field_type_mapping.get(champ.type_champ, FieldType.TEXT_SHORT)
        
        # Parser les contraintes JSON
        contraintes = {}
        if champ.contraintes:
            try:
                contraintes = json.loads(champ.contraintes)
            except json.JSONDecodeError:
                logger.warning(f"Contraintes JSON invalides pour le champ {champ.nom}")
        
        # Créer la configuration
        config = FieldValidationConfig(
            field_type=field_type,
            required=bool(champ.obligatoire),
            placeholder=champ.placeholder,
            help_text=champ.description
        )
        
        # Appliquer les contraintes spécifiques
        if 'min_length' in contraintes:
            config.min_length = int(contraintes['min_length'])
        
        if 'max_length' in contraintes:
            config.max_length = int(contraintes['max_length'])
        
        if 'min_value' in contraintes:
            config.min_value = float(contraintes['min_value'])
        
        if 'max_value' in contraintes:
            config.max_value = float(contraintes['max_value'])
        
        if 'pattern' in contraintes:
            config.pattern = contraintes['pattern']
        
        # Options pour select/radio
        if 'options' in contraintes:
            config.options = contraintes['options']
        
        # Configuration spécifique pour les fichiers
        if field_type == FieldType.FILE:
            if 'allowed_extensions' in contraintes:
                config.allowed_extensions = contraintes['allowed_extensions']
            if 'max_file_size' in contraintes:
                config.max_file_size = int(contraintes['max_file_size'])
        
        # Messages d'erreur personnalisés
        if 'error_messages' in contraintes:
            config.error_messages = contraintes['error_messages']
        
        return config
    
    async def validate_soumission(self, formulaire_id: int, soumission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide une soumission de formulaire"""
        
        # Récupérer la configuration de validation
        validation_config = await self.get_form_validation_config(formulaire_id)
        
        # Valider avec le moteur
        result = self.engine.validate_form(soumission_data, validation_config)
        
        # Enrichir le résultat avec des informations contextuelles
        result['formulaire_id'] = formulaire_id
        result['timestamp'] = str(datetime.utcnow())
        
        # Log des résultats pour monitoring
        if not result['valid']:
            logger.warning(f"Validation échouée pour formulaire {formulaire_id}: {result['errors']}")
        else:
            logger.info(f"Validation réussie pour formulaire {formulaire_id}")
        
        return result
    
    def get_template_validation_config(self, template: FormTemplate) -> Dict[str, FieldValidationConfig]:
        """Récupère la configuration de validation pour un template prédéfini"""
        return self.engine.templates.get(template, {})
    
    def create_validation_schema(self, form_config: Dict[str, FieldValidationConfig]) -> Dict[str, Any]:
        """Génère un schéma de validation JSON pour le frontend"""
        schema = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
        
        for field_name, config in form_config.items():
            field_schema = self._create_field_schema(config)
            schema["properties"][field_name] = field_schema
            
            if config.required:
                schema["required"].append(field_name)
        
        return schema
    
    def _create_field_schema(self, config: FieldValidationConfig) -> Dict[str, Any]:
        """Crée un schéma JSON Schema pour un champ"""
        schema: Dict[str, Any] = {"type": "string"}  # Par défaut
        
        # Type selon le FieldType
        if config.field_type == FieldType.NUMBER:
            schema["type"] = "number"
            if config.min_value is not None:
                schema["minimum"] = config.min_value
            if config.max_value is not None:
                schema["maximum"] = config.max_value
        
        elif config.field_type == FieldType.EMAIL:
            schema["format"] = "email"
        
        elif config.field_type == FieldType.URL:
            schema["format"] = "uri"
        
        elif config.field_type == FieldType.DATE:
            schema["format"] = "date"
        
        elif config.field_type == FieldType.DATETIME:
            schema["format"] = "date-time"
        
        elif config.field_type in [FieldType.SELECT_MULTIPLE, FieldType.CHECKBOX]:
            schema["type"] = "array"
            if config.options:
                schema["items"] = {"enum": config.options}
        
        # Contraintes de longueur
        if config.min_length is not None:
            schema["minLength"] = config.min_length
        
        if config.max_length is not None:
            schema["maxLength"] = config.max_length
        
        # Pattern
        if config.pattern:
            schema["pattern"] = config.pattern
        
        # Options pour select
        if config.options and config.field_type == FieldType.SELECT_SINGLE:
            schema["enum"] = config.options
        
        # Métadonnées
        if config.placeholder:
            schema["title"] = config.placeholder
        
        if config.help_text:
            schema["description"] = config.help_text
        
        return schema

class ValidationMiddleware:
    """Middleware pour validation automatique des soumissions"""
    
    def __init__(self):
        self.validation_cache = {}  # Cache des configurations de validation
    
    async def validate_soumission_middleware(
        self, 
        formulaire_id: int, 
        soumission_data: Dict[str, Any], 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Middleware de validation pour les soumissions"""
        
        # Vérifier le cache
        cache_key = f"form_{formulaire_id}"
        
        if cache_key not in self.validation_cache:
            service = DynamicFormValidationService(db)
            config = await service.get_form_validation_config(formulaire_id)
            self.validation_cache[cache_key] = config
        else:
            config = self.validation_cache[cache_key]
        
        # Validation avec le moteur
        engine = FormValidationEngine()
        return engine.validate_form(soumission_data, config)
    
    def clear_cache(self, formulaire_id: Optional[int] = None):
        """Efface le cache de validation"""
        if formulaire_id:
            cache_key = f"form_{formulaire_id}"
            self.validation_cache.pop(cache_key, None)
        else:
            self.validation_cache.clear()

# Instance globale du middleware
validation_middleware = ValidationMiddleware()

# Utilitaires pour l'intégration

def get_validation_errors_for_frontend(validation_result: Dict[str, Any]) -> Dict[str, Any]:
    """Formate les erreurs de validation pour le frontend"""
    return {
        "valid": validation_result["valid"],
        "errors": validation_result.get("errors", {}),
        "warnings": validation_result.get("warnings", {}),
        "field_count": validation_result.get("summary", {}).get("total_fields", 0),
        "error_count": validation_result.get("summary", {}).get("error_count", 0)
    }

def create_form_from_template(template: FormTemplate, db: AsyncSession) -> Dict[str, Any]:
    """Crée un formulaire à partir d'un template prédéfini"""
    engine = FormValidationEngine()
    config = engine.templates.get(template, {})
    
    form_structure = {
        "name": f"Formulaire {template.value}",
        "template": template.value,
        "fields": []
    }
    
    for field_name, field_config in config.items():
        field_structure = {
            "name": field_name,
            "type": field_config.field_type.value,
            "required": field_config.required,
            "placeholder": field_config.placeholder,
            "help_text": field_config.help_text,
            "constraints": {
                "min_length": field_config.min_length,
                "max_length": field_config.max_length,
                "min_value": field_config.min_value,
                "max_value": field_config.max_value,
                "pattern": field_config.pattern,
                "options": field_config.options,
            }
        }
        form_structure["fields"].append(field_structure)
    
    return form_structure