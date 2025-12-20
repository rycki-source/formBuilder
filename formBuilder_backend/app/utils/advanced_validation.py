"""
Système de Validation Avancé pour FormBuilder
Module de validation dynamique et extensible pour tous types de formulaires
"""

from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, date
import re
import json
from pydantic import BaseModel, Field, validator

class FormStructureType(Enum):
    """Types de structures de formulaires supportées"""
    SIMPLE = "simple"              # Tous champs visibles, validation temps réel
    MULTI_STEP = "multi_step"      # Plusieurs étapes, validation par étape
    WIZARD = "wizard"              # Processus guidé avec logique conditionnelle
    DYNAMIC = "dynamic"            # Formulaire généré dynamiquement

class FieldType(Enum):
    """Types de champs supportés avec leurs validations spécifiques"""
    TEXT_SHORT = "text_short"      # Texte court (nom, prénom, etc.)
    TEXT_LONG = "text_long"        # Texte long (description, message)
    EMAIL = "email"                # Email avec validation RFC
    PHONE = "phone"                # Téléphone avec format local
    PASSWORD = "password"          # Mot de passe avec règles de sécurité
    NUMBER = "number"              # Nombre entier ou décimal
    DATE = "date"                  # Date avec format et plage
    TIME = "time"                  # Heure au format 24h
    DATETIME = "datetime"          # Date et heure combinées
    URL = "url"                    # URL valide
    FILE = "file"                  # Upload de fichier
    SELECT_SINGLE = "select_single" # Sélection unique
    SELECT_MULTIPLE = "select_multiple" # Sélection multiple
    CHECKBOX = "checkbox"          # Case à cocher
    RADIO = "radio"               # Bouton radio
    POSTAL_CODE = "postal_code"   # Code postal
    IBAN = "iban"                 # IBAN bancaire
    SIRET = "siret"               # SIRET français
    VAT_NUMBER = "vat_number"     # Numéro de TVA

class FormTemplate(Enum):
    """Templates de formulaires prédéfinis"""
    CONTACT = "contact"
    REGISTRATION = "registration"
    LOGIN = "login"
    ORDER = "order"
    FEEDBACK = "feedback"
    APPLICATION = "application"
    LEAD_GENERATION = "lead_generation"
    RESERVATION = "reservation"
    SURVEY = "survey"
    NEWSLETTER = "newsletter"

@dataclass
class ValidationRule:
    """Règle de validation individuelle"""
    name: str
    message: str
    validator: Callable[[Any], bool]
    level: str = "error"  # error, warning, info

@dataclass
class FieldValidationConfig:
    """Configuration de validation pour un champ"""
    field_type: FieldType
    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    custom_rules: Optional[List[ValidationRule]] = None
    allowed_extensions: Optional[List[str]] = None  # Pour les fichiers
    max_file_size: Optional[int] = None   # En octets
    options: Optional[List[str]] = None             # Pour select/radio
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    error_messages: Optional[Dict[str, str]] = None

class FormValidationEngine:
    """Moteur de validation principal pour FormBuilder"""
    
    def __init__(self):
        self.validators = self._initialize_validators()
        self.templates = self._initialize_templates()
    
    def _initialize_validators(self) -> Dict[FieldType, Callable]:
        """Initialise les validateurs pour chaque type de champ"""
        return {
            FieldType.TEXT_SHORT: self._validate_text_short,
            FieldType.TEXT_LONG: self._validate_text_long,
            FieldType.EMAIL: self._validate_email,
            FieldType.PHONE: self._validate_phone,
            FieldType.PASSWORD: self._validate_password,
            FieldType.NUMBER: self._validate_number,
            FieldType.DATE: self._validate_date,
            FieldType.TIME: self._validate_time,
            FieldType.DATETIME: self._validate_datetime,
            FieldType.URL: self._validate_url,
            FieldType.FILE: self._validate_file,
            FieldType.SELECT_SINGLE: self._validate_select_single,
            FieldType.SELECT_MULTIPLE: self._validate_select_multiple,
            FieldType.CHECKBOX: self._validate_checkbox,
            FieldType.RADIO: self._validate_radio,
            FieldType.POSTAL_CODE: self._validate_postal_code,
            FieldType.IBAN: self._validate_iban,
            FieldType.SIRET: self._validate_siret,
            FieldType.VAT_NUMBER: self._validate_vat_number,
        }
    
    def _initialize_templates(self) -> Dict[FormTemplate, Dict[str, FieldValidationConfig]]:
        """Initialise les templates de formulaires prédéfinis"""
        return {
            FormTemplate.CONTACT: self._create_contact_template(),
            FormTemplate.REGISTRATION: self._create_registration_template(),
            FormTemplate.LOGIN: self._create_login_template(),
            FormTemplate.ORDER: self._create_order_template(),
            FormTemplate.FEEDBACK: self._create_feedback_template(),
            FormTemplate.APPLICATION: self._create_application_template(),
            FormTemplate.LEAD_GENERATION: self._create_lead_generation_template(),
            FormTemplate.RESERVATION: self._create_reservation_template(),
        }
    
    def get_form_template(self, template: FormTemplate) -> Dict[str, FieldValidationConfig]:
        """Retourne la configuration de validation pour un template donné"""
        template_mapping = {
            FormTemplate.CONTACT: self._create_contact_template(),
            FormTemplate.REGISTRATION: self._create_registration_template(),
            FormTemplate.LOGIN: self._create_login_template(),
            FormTemplate.ORDER: self._create_order_template(),
            FormTemplate.FEEDBACK: self._create_feedback_template(),
            FormTemplate.APPLICATION: self._create_application_template(),
            FormTemplate.LEAD_GENERATION: self._create_lead_generation_template(),
            FormTemplate.RESERVATION: self._create_reservation_template()
        }
        return template_mapping.get(template, {})

    def validate_field(self, field_name: str, value: Any, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide un champ individuel"""
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Validation requis
        if config.required and (value is None or value == ""):
            result["valid"] = False
            result["errors"].append(f"{field_name} est requis")
            return result
        
        # Si le champ n'est pas requis et vide, on considère comme valide
        if not config.required and (value is None or value == ""):
            return result
        
        # Validation spécifique au type
        validator = self.validators.get(config.field_type)
        if validator:
            type_result = validator(value, config)
            if not type_result["valid"]:
                result["valid"] = False
                result["errors"].extend(type_result.get("errors", []))
                result["warnings"].extend(type_result.get("warnings", []))
        
        # Validation des règles personnalisées
        if config.custom_rules:
            for rule in config.custom_rules:
                if not rule.validator(value):
                    if rule.level == "error":
                        result["valid"] = False
                        result["errors"].append(rule.message)
                    elif rule.level == "warning":
                        result["warnings"].append(rule.message)
        
        return result
    
    def validate_form(self, form_data: Dict[str, Any], form_config: Dict[str, FieldValidationConfig]) -> Dict[str, Any]:
        """Valide un formulaire complet"""
        result = {
            "valid": True,
            "errors": {},
            "warnings": {},
            "suggestions": {},
            "summary": {
                "total_fields": len(form_config),
                "valid_fields": 0,
                "error_count": 0,
                "warning_count": 0
            }
        }
        
        for field_name, config in form_config.items():
            value = form_data.get(field_name)
            field_result = self.validate_field(field_name, value, config)
            
            if not field_result["valid"]:
                result["valid"] = False
                result["errors"][field_name] = field_result["errors"]
                result["summary"]["error_count"] += len(field_result["errors"])
            else:
                result["summary"]["valid_fields"] += 1
            
            if field_result.get("warnings"):
                result["warnings"][field_name] = field_result["warnings"]
                result["summary"]["warning_count"] += len(field_result["warnings"])
            
            if field_result.get("suggestions"):
                result["suggestions"][field_name] = field_result["suggestions"]
        
        return result
    
    # Validateurs spécifiques par type de champ
    
    def _validate_text_short(self, value: str, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide un champ texte court (nom, prénom, titre, etc.)"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if not isinstance(value, str):
            result["valid"] = False
            result["errors"].append("Doit être du texte")
            return result
        
        value = value.strip()
        
        # Longueur
        if config.min_length and len(value) < config.min_length:
            result["valid"] = False
            result["errors"].append(f"Minimum {config.min_length} caractères")
        
        if config.max_length and len(value) > config.max_length:
            result["valid"] = False
            result["errors"].append(f"Maximum {config.max_length} caractères")
        
        # Pattern personnalisé ou pattern par défaut pour nom/prénom
        pattern = config.pattern or r"^[a-zA-ZÀ-ÿ\s\-'\.]+$"
        if not re.match(pattern, value):
            result["valid"] = False
            result["errors"].append("Contient des caractères non autorisés")
        
        # Vérification des espaces multiples
        if "  " in value:
            result["warnings"].append("Contient des espaces multiples")
        
        return result
    
    def _validate_text_long(self, value: str, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide un champ texte long (description, message, commentaire)"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if not isinstance(value, str):
            result["valid"] = False
            result["errors"].append("Doit être du texte")
            return result
        
        value = value.strip()
        
        # Longueur
        if config.min_length and len(value) < config.min_length:
            result["valid"] = False
            result["errors"].append(f"Minimum {config.min_length} caractères")
        
        if config.max_length and len(value) > config.max_length:
            result["valid"] = False
            result["errors"].append(f"Maximum {config.max_length} caractères")
        
        # Détection de spam basique
        if len(value) > 50:
            # Trop de majuscules
            upper_ratio = sum(1 for c in value if c.isupper()) / len(value)
            if upper_ratio > 0.7:
                result["warnings"].append("Trop de majuscules détectées")
            
            # Répétitions excessives
            if re.search(r'(.)\1{4,}', value):
                result["warnings"].append("Caractères répétés détectés")
        
        return result
    
    def _validate_email(self, value: str, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide une adresse email selon RFC 5322"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if not isinstance(value, str):
            result["valid"] = False
            result["errors"].append("Doit être du texte")
            return result
        
        value = value.strip().lower()
        
        # Pattern email renforcé
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            result["valid"] = False
            result["errors"].append("Format d'adresse email invalide")
            return result
        
        # Vérifications supplémentaires
        if '..' in value:
            result["valid"] = False
            result["errors"].append("Ne peut pas contenir de points consécutifs")
        
        if value.startswith('.') or value.startswith('-'):
            result["valid"] = False
            result["errors"].append("Ne peut pas commencer par un point ou un tiret")
        
        # Longueur maximale
        if len(value) > 320:
            result["valid"] = False
            result["errors"].append("Adresse email trop longue (max 320 caractères)")
        
        # Domaines temporaires (warning)
        temp_domains = ['10minutemail.com', 'guerrillamail.com', 'tempmail.org', 'throwaway.email']
        domain = value.split('@')[1] if '@' in value else ''
        if domain in temp_domains:
            result["warnings"].append("Adresse email temporaire détectée")
        
        return result
    
    def _validate_phone(self, value: str, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide un numéro de téléphone (format français par défaut)"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if not isinstance(value, str):
            result["valid"] = False
            result["errors"].append("Doit être du texte")
            return result
        
        # Nettoyage
        cleaned = re.sub(r'[\s\-\.\(\)]', '', value)
        
        # Pattern français par défaut
        pattern = config.pattern or r'^(?:\+33|0)[1-9](?:[0-9]{8})$'
        
        if not re.match(pattern, cleaned):
            result["valid"] = False
            result["errors"].append("Format de téléphone invalide (ex: 06 12 34 56 78)")
        
        # Vérification de longueur
        if len(cleaned) < 10 or len(cleaned) > 15:
            result["valid"] = False
            result["errors"].append("Longueur invalide (10-15 chiffres)")
        
        return result
    
    def _validate_password(self, value: str, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide un mot de passe avec règles de sécurité strictes"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if not isinstance(value, str):
            result["valid"] = False
            result["errors"].append("Doit être du texte")
            return result
        
        # Utilisation du validateur existant
        from app.utils.validation import PasswordValidator
        validation_result = PasswordValidator.validate_password(value)
        
        if not validation_result.is_valid:
            result["valid"] = False
            result["errors"].extend(validation_result.errors)
        
        # Note: calcul de force simplifié
        if result["valid"] and len(value) < 12:
            result["warnings"].append("Considérez un mot de passe plus long pour une sécurité renforcée")
        
        return result
    
    def _validate_number(self, value: Union[str, int, float], config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide un nombre (entier ou décimal)"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        try:
            if isinstance(value, str):
                # Tentative de conversion
                if '.' in value or ',' in value:
                    num_value = float(value.replace(',', '.'))
                else:
                    num_value = int(value)
            else:
                num_value = float(value) if isinstance(value, (int, float)) else None
                
            if num_value is None:
                raise ValueError("Conversion impossible")
                
        except (ValueError, TypeError):
            result["valid"] = False
            result["errors"].append("Doit être un nombre valide")
            return result
        
        # Validation des plages
        if config.min_value is not None and num_value < config.min_value:
            result["valid"] = False
            result["errors"].append(f"Valeur minimum: {config.min_value}")
        
        if config.max_value is not None and num_value > config.max_value:
            result["valid"] = False
            result["errors"].append(f"Valeur maximum: {config.max_value}")
        
        return result
    
    def _validate_date(self, value: Union[str, date], config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide une date"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        try:
            if isinstance(value, str):
                # Formats supportés
                date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
                parsed_date = None
                
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(value, fmt).date()
                        break
                    except ValueError:
                        continue
                
                if parsed_date is None:
                    raise ValueError("Format non reconnu")
                    
            elif isinstance(value, date):
                parsed_date = value
            else:
                raise ValueError("Type non supporté")
                
        except ValueError:
            result["valid"] = False
            result["errors"].append("Date invalide (format: JJ/MM/AAAA)")
            return result
        
        # Validation des plages (si configurées)
        today = date.today()
        
        # Age minimum (pour dates de naissance)
        if config.min_value and isinstance(config.min_value, int):
            min_date = date(today.year - config.min_value, today.month, today.day)
            if parsed_date > min_date:
                result["valid"] = False
                result["errors"].append(f"Age minimum requis: {config.min_value} ans")
        
        # Date future interdite (par défaut pour dates de naissance)
        if parsed_date > today:
            result["warnings"].append("Date dans le futur")
        
        return result
    
    def _validate_postal_code(self, value: str, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide un code postal (français par défaut)"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if not isinstance(value, str):
            result["valid"] = False
            result["errors"].append("Doit être du texte")
            return result
        
        value = value.strip()
        
        # Pattern français par défaut (5 chiffres)
        pattern = config.pattern or r'^[0-9]{5}$'
        
        if not re.match(pattern, value):
            result["valid"] = False
            result["errors"].append("Code postal invalide (5 chiffres)")
        
        # Vérification des codes postaux spéciaux
        if value.startswith('00') or value.startswith('96') or value.startswith('97') or value.startswith('98'):
            result["warnings"].append("Code postal DOM-TOM ou étranger")
        
        return result
    
    # Templates de formulaires prédéfinis
    
    def _create_contact_template(self) -> Dict[str, FieldValidationConfig]:
        """Template pour formulaire de contact"""
        return {
            "prenom": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50,
                placeholder="Votre prénom",
                error_messages={"required": "Le prénom est requis"}
            ),
            "nom": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50,
                placeholder="Votre nom de famille"
            ),
            "email": FieldValidationConfig(
                field_type=FieldType.EMAIL,
                required=True,
                placeholder="votre.email@example.com"
            ),
            "telephone": FieldValidationConfig(
                field_type=FieldType.PHONE,
                required=False,
                placeholder="06 12 34 56 78"
            ),
            "sujet": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=5,
                max_length=100,
                placeholder="Sujet de votre message"
            ),
            "message": FieldValidationConfig(
                field_type=FieldType.TEXT_LONG,
                required=True,
                min_length=20,
                max_length=2000,
                placeholder="Votre message..."
            )
        }
    
    def _create_registration_template(self) -> Dict[str, FieldValidationConfig]:
        """Template pour formulaire d'inscription"""
        return {
            "username": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=3,
                max_length=20,
                pattern=r'^[a-zA-Z0-9_]+$',
                placeholder="nom_utilisateur"
            ),
            "email": FieldValidationConfig(
                field_type=FieldType.EMAIL,
                required=True,
                placeholder="votre@email.com"
            ),
            "mot_de_passe": FieldValidationConfig(
                field_type=FieldType.PASSWORD,
                required=True,
                min_length=8,
                placeholder="••••••••"
            ),
            "confirmation_mot_de_passe": FieldValidationConfig(
                field_type=FieldType.PASSWORD,
                required=True,
                placeholder="••••••••"
            ),
            "nom": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50
            ),
            "prenom": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50
            ),
            "date_naissance": FieldValidationConfig(
                field_type=FieldType.DATE,
                required=True,
                min_value=13  # Age minimum
            ),
            "conditions": FieldValidationConfig(
                field_type=FieldType.CHECKBOX,
                required=True,
                error_messages={"required": "Vous devez accepter les conditions d'utilisation"}
            )
        }
    
    def _validate_time(self, value: Union[str, datetime], config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide une heure (format 24h)"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if isinstance(value, str):
            # Format HH:MM ou HH:MM:SS
            time_pattern = r'^([01]?[0-9]|2[0-3]):([0-5][0-9])(?::([0-5][0-9]))?$'
            if not re.match(time_pattern, value):
                result["valid"] = False
                result["errors"].append("Format d'heure invalide (HH:MM)")
        
        return result
    
    def _validate_datetime(self, value: Union[str, datetime], config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide une date et heure"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        try:
            if isinstance(value, str):
                # Formats supportés pour datetime
                dt_formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y %H:%M']
                parsed_dt = None
                
                for fmt in dt_formats:
                    try:
                        parsed_dt = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue
                
                if parsed_dt is None:
                    raise ValueError("Format non reconnu")
            elif isinstance(value, datetime):
                parsed_dt = value
            else:
                raise ValueError("Type non supporté")
        except ValueError:
            result["valid"] = False
            result["errors"].append("Date et heure invalides (format: JJ/MM/AAAA HH:MM)")
        
        return result
    
    def _validate_url(self, value: str, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide une URL"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if not isinstance(value, str):
            result["valid"] = False
            result["errors"].append("Doit être du texte")
            return result
        
        value = value.strip()
        
        # Pattern URL basique
        url_pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        if not re.match(url_pattern, value):
            result["valid"] = False
            result["errors"].append("URL invalide (doit commencer par http:// ou https://)")
        
        return result
    
    def _validate_file(self, value: Any, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide un fichier uploadé"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if value is None:
            return result
        
        # Vérification des extensions autorisées
        if config.allowed_extensions and hasattr(value, 'filename'):
            filename = value.filename.lower()
            if not any(filename.endswith(ext.lower()) for ext in config.allowed_extensions):
                result["valid"] = False
                result["errors"].append(f"Extension non autorisée. Formats acceptés: {', '.join(config.allowed_extensions)}")
        
        # Vérification de la taille
        if config.max_file_size and hasattr(value, 'size'):
            if value.size > config.max_file_size:
                result["valid"] = False
                result["errors"].append(f"Fichier trop volumineux (max: {config.max_file_size // 1024 // 1024}MB)")
        
        return result
    
    def _validate_select_single(self, value: str, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide une sélection unique"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if config.options and value not in config.options:
            result["valid"] = False
            result["errors"].append("Sélection invalide")
        
        return result
    
    def _validate_select_multiple(self, value: List[str], config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide une sélection multiple"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if not isinstance(value, list):
            result["valid"] = False
            result["errors"].append("Doit être une liste")
            return result
        
        if config.options:
            invalid_options = [v for v in value if v not in config.options]
            if invalid_options:
                result["valid"] = False
                result["errors"].append(f"Sélections invalides: {', '.join(invalid_options)}")
        
        return result
    
    def _validate_checkbox(self, value: Union[bool, str], config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide une case à cocher"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if config.required:
            if isinstance(value, bool) and not value:
                result["valid"] = False
                result["errors"].append("Cette case doit être cochée")
            elif isinstance(value, str) and value.lower() not in ['true', '1', 'on']:
                result["valid"] = False
                result["errors"].append("Cette case doit être cochée")
        
        return result
    
    def _validate_radio(self, value: str, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide un bouton radio"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if config.options and value not in config.options:
            result["valid"] = False
            result["errors"].append("Sélection invalide")
        
        return result
    
    def _validate_iban(self, value: str, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide un IBAN"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if not isinstance(value, str):
            result["valid"] = False
            result["errors"].append("Doit être du texte")
            return result
        
        # Nettoyage
        iban = value.replace(' ', '').upper()
        
        # Longueur pour la France (27 caractères)
        if len(iban) != 27:
            result["valid"] = False
            result["errors"].append("IBAN français doit contenir 27 caractères")
            return result
        
        # Pattern français
        if not iban.startswith('FR') or not iban[2:].isdigit():
            result["valid"] = False
            result["errors"].append("Format IBAN français invalide (FR + 25 chiffres)")
        
        return result
    
    def _validate_siret(self, value: str, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide un numéro SIRET"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if not isinstance(value, str):
            result["valid"] = False
            result["errors"].append("Doit être du texte")
            return result
        
        # Nettoyage
        siret = value.replace(' ', '').replace('.', '')
        
        # Longueur (14 chiffres)
        if len(siret) != 14 or not siret.isdigit():
            result["valid"] = False
            result["errors"].append("SIRET doit contenir 14 chiffres")
            return result
        
        # Algorithme de validation SIRET (simplifié)
        # Les 9 premiers chiffres = SIREN, les 5 suivants = NIC
        siren = siret[:9]
        nic = siret[9:]
        
        # Validation basique (peut être améliorée)
        if nic == "00000":
            result["warnings"].append("NIC potentiellement invalide")
        
        return result
    
    def _validate_vat_number(self, value: str, config: FieldValidationConfig) -> Dict[str, Any]:
        """Valide un numéro de TVA intracommunautaire"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if not isinstance(value, str):
            result["valid"] = False
            result["errors"].append("Doit être du texte")
            return result
        
        value = value.replace(' ', '').upper()
        
        # Pattern français: FR + 11 chiffres
        french_pattern = r'^FR[0-9]{11}$'
        # Pattern européen général: 2 lettres + chiffres/lettres
        eu_pattern = r'^[A-Z]{2}[A-Z0-9]+$'
        
        if re.match(french_pattern, value):
            # Validation française spécifique
            pass
        elif re.match(eu_pattern, value):
            # Numéro européen valide
            result["warnings"].append("Numéro de TVA européen non français")
        else:
            result["valid"] = False
            result["errors"].append("Format de numéro de TVA invalide")
        
        return result
    
    def _create_login_template(self) -> Dict[str, FieldValidationConfig]:
        """Template pour formulaire de connexion"""
        return {
            "identifiant": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=3,
                placeholder="Email ou nom d'utilisateur"
            ),
            "mot_de_passe": FieldValidationConfig(
                field_type=FieldType.PASSWORD,
                required=True,
                min_length=1,  # Pas de validation stricte sur la connexion
                placeholder="••••••••"
            ),
            "se_souvenir": FieldValidationConfig(
                field_type=FieldType.CHECKBOX,
                required=False
            )
        }
    
    def _create_order_template(self) -> Dict[str, FieldValidationConfig]:
        """Template pour formulaire de commande"""
        return {
            # Informations personnelles
            "nom": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50
            ),
            "prenom": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50
            ),
            "email": FieldValidationConfig(
                field_type=FieldType.EMAIL,
                required=True
            ),
            "telephone": FieldValidationConfig(
                field_type=FieldType.PHONE,
                required=True
            ),
            
            # Adresse de livraison
            "adresse_rue": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=5,
                max_length=100,
                placeholder="Numéro et nom de rue"
            ),
            "adresse_complement": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=False,
                max_length=100,
                placeholder="Bâtiment, étage, etc."
            ),
            "code_postal": FieldValidationConfig(
                field_type=FieldType.POSTAL_CODE,
                required=True
            ),
            "ville": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50,
                pattern=r'^[a-zA-ZÀ-ÿ\s\-\']+$'
            ),
            "pays": FieldValidationConfig(
                field_type=FieldType.SELECT_SINGLE,
                required=True,
                options=["France", "Belgique", "Suisse", "Canada", "Autre"]
            ),
            
            # Facturation
            "facturation_identique": FieldValidationConfig(
                field_type=FieldType.CHECKBOX,
                required=False
            ),
            
            # Paiement
            "mode_paiement": FieldValidationConfig(
                field_type=FieldType.RADIO,
                required=True,
                options=["Carte bancaire", "PayPal", "Virement", "Chèque"]
            ),
            
            # Carte bancaire (si sélectionnée)
            "numero_carte": FieldValidationConfig(
                field_type=FieldType.NUMBER,
                required=False,
                pattern=r'^[0-9]{13,19}$',
                placeholder="1234 5678 9012 3456"
            ),
            "nom_carte": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=False,
                min_length=2,
                max_length=50
            ),
            "expiration_carte": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=False,
                pattern=r'^(0[1-9]|1[0-2])\/[0-9]{2}$',
                placeholder="MM/AA"
            ),
            "cvv": FieldValidationConfig(
                field_type=FieldType.NUMBER,
                required=False,
                pattern=r'^[0-9]{3,4}$',
                placeholder="123"
            )
        }
    
    def _create_feedback_template(self) -> Dict[str, FieldValidationConfig]:
        """Template pour formulaire de feedback"""
        return {
            "email": FieldValidationConfig(
                field_type=FieldType.EMAIL,
                required=False,
                placeholder="email@example.com (optionnel pour réponse)"
            ),
            "note": FieldValidationConfig(
                field_type=FieldType.SELECT_SINGLE,
                required=True,
                options=["1", "2", "3", "4", "5"]
            ),
            "categorie": FieldValidationConfig(
                field_type=FieldType.SELECT_SINGLE,
                required=True,
                options=["Bug", "Suggestion", "Compliment", "Question", "Autre"]
            ),
            "titre": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=5,
                max_length=100,
                placeholder="Titre de votre feedback"
            ),
            "description": FieldValidationConfig(
                field_type=FieldType.TEXT_LONG,
                required=True,
                min_length=10,
                max_length=1000,
                placeholder="Décrivez votre expérience..."
            ),
            "piece_jointe": FieldValidationConfig(
                field_type=FieldType.FILE,
                required=False,
                allowed_extensions=[".jpg", ".png", ".pdf"],
                max_file_size=5 * 1024 * 1024  # 5MB
            )
        }
    
    def _create_application_template(self) -> Dict[str, FieldValidationConfig]:
        """Template pour formulaire de candidature"""
        return {
            # Informations personnelles
            "civilite": FieldValidationConfig(
                field_type=FieldType.SELECT_SINGLE,
                required=True,
                options=["M.", "Mme", "Mlle"]
            ),
            "nom": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50
            ),
            "prenom": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50
            ),
            "email": FieldValidationConfig(
                field_type=FieldType.EMAIL,
                required=True
            ),
            "telephone": FieldValidationConfig(
                field_type=FieldType.PHONE,
                required=True
            ),
            
            # Expérience
            "poste_actuel": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=100,
                placeholder="Votre poste actuel ou précédent"
            ),
            "entreprise_actuelle": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=100
            ),
            "annees_experience": FieldValidationConfig(
                field_type=FieldType.NUMBER,
                required=True,
                min_value=0,
                max_value=50
            ),
            
            # Formation
            "dernier_diplome": FieldValidationConfig(
                field_type=FieldType.SELECT_SINGLE,
                required=True,
                options=["Bac", "Bac+2", "Bac+3", "Bac+5", "Doctorat", "Autre"]
            ),
            "etablissement": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=100
            ),
            "annee_diplome": FieldValidationConfig(
                field_type=FieldType.NUMBER,
                required=True,
                min_value=1950,
                max_value=datetime.now().year
            ),
            
            # Candidature
            "poste_vise": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=100
            ),
            "lettre_motivation": FieldValidationConfig(
                field_type=FieldType.TEXT_LONG,
                required=True,
                min_length=100,
                max_length=5000,
                placeholder="Votre lettre de motivation..."
            ),
            "cv": FieldValidationConfig(
                field_type=FieldType.FILE,
                required=True,
                allowed_extensions=[".pdf", ".doc", ".docx"],
                max_file_size=5 * 1024 * 1024  # 5MB
            ),
            "disponibilite": FieldValidationConfig(
                field_type=FieldType.SELECT_SINGLE,
                required=True,
                options=["Immédiate", "1 mois", "2 mois", "3 mois", "À négocier"]
            ),
            "pretentions_salariales": FieldValidationConfig(
                field_type=FieldType.NUMBER,
                required=False,
                min_value=0,
                placeholder="Salaire annuel brut en euros (optionnel)"
            )
        }
    
    def _create_lead_generation_template(self) -> Dict[str, FieldValidationConfig]:
        """Template pour génération de leads"""
        return {
            # Entreprise
            "nom_entreprise": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=100
            ),
            "secteur_activite": FieldValidationConfig(
                field_type=FieldType.SELECT_SINGLE,
                required=True,
                options=["Technologie", "Finance", "Santé", "Éducation", "Commerce", "Industrie", "Services", "Autre"]
            ),
            "taille_entreprise": FieldValidationConfig(
                field_type=FieldType.SELECT_SINGLE,
                required=True,
                options=["1-10 employés", "11-50 employés", "51-200 employés", "200+ employés"]
            ),
            "site_web": FieldValidationConfig(
                field_type=FieldType.URL,
                required=False,
                placeholder="https://www.example.com"
            ),
            
            # Contact
            "nom_contact": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50
            ),
            "prenom_contact": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50
            ),
            "fonction": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=100,
                placeholder="Votre fonction dans l'entreprise"
            ),
            "email_professionnel": FieldValidationConfig(
                field_type=FieldType.EMAIL,
                required=True,
                placeholder="contact@entreprise.com"
            ),
            "telephone_direct": FieldValidationConfig(
                field_type=FieldType.PHONE,
                required=True
            ),
            
            # Projet
            "type_projet": FieldValidationConfig(
                field_type=FieldType.SELECT_MULTIPLE,
                required=True,
                options=["Développement web", "Application mobile", "Consulting", "Formation", "Support", "Autre"]
            ),
            "budget_estime": FieldValidationConfig(
                field_type=FieldType.SELECT_SINGLE,
                required=False,
                options=["< 10k€", "10k-50k€", "50k-100k€", "100k-500k€", "> 500k€", "À définir"]
            ),
            "delai_souhaite": FieldValidationConfig(
                field_type=FieldType.SELECT_SINGLE,
                required=True,
                options=["Urgent (< 1 mois)", "Court terme (1-3 mois)", "Moyen terme (3-6 mois)", "Long terme (> 6 mois)"]
            ),
            "description_besoin": FieldValidationConfig(
                field_type=FieldType.TEXT_LONG,
                required=True,
                min_length=50,
                max_length=1000,
                placeholder="Décrivez votre besoin en détail..."
            ),
            
            # Consentements RGPD
            "consentement_rgpd": FieldValidationConfig(
                field_type=FieldType.CHECKBOX,
                required=True,
                error_messages={"required": "Vous devez accepter le traitement de vos données personnelles"}
            ),
            "consentement_email": FieldValidationConfig(
                field_type=FieldType.CHECKBOX,
                required=False
            ),
            "consentement_telephone": FieldValidationConfig(
                field_type=FieldType.CHECKBOX,
                required=False
            )
        }
    
    def _create_reservation_template(self) -> Dict[str, FieldValidationConfig]:
        """Template pour formulaire de réservation"""
        return {
            # Type et dates
            "type_reservation": FieldValidationConfig(
                field_type=FieldType.SELECT_SINGLE,
                required=True,
                options=["Chambre simple", "Chambre double", "Suite", "Table restaurant", "Salle de réunion", "Autre"]
            ),
            "date_arrivee": FieldValidationConfig(
                field_type=FieldType.DATE,
                required=True
            ),
            "date_depart": FieldValidationConfig(
                field_type=FieldType.DATE,
                required=True
            ),
            "heure_arrivee": FieldValidationConfig(
                field_type=FieldType.TIME,
                required=False,
                placeholder="14:00"
            ),
            "nombre_personnes": FieldValidationConfig(
                field_type=FieldType.NUMBER,
                required=True,
                min_value=1,
                max_value=10
            ),
            
            # Informations client
            "nom_client": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50
            ),
            "prenom_client": FieldValidationConfig(
                field_type=FieldType.TEXT_SHORT,
                required=True,
                min_length=2,
                max_length=50
            ),
            "email_client": FieldValidationConfig(
                field_type=FieldType.EMAIL,
                required=True
            ),
            "telephone_client": FieldValidationConfig(
                field_type=FieldType.PHONE,
                required=True
            ),
            
            # Préférences
            "preferences_speciales": FieldValidationConfig(
                field_type=FieldType.TEXT_LONG,
                required=False,
                max_length=500,
                placeholder="Demandes particulières, allergies, etc."
            ),
            "options_extras": FieldValidationConfig(
                field_type=FieldType.SELECT_MULTIPLE,
                required=False,
                options=["Petit-déjeuner", "Parking", "Wi-Fi", "Room service", "Spa", "Salle de sport"]
            ),
            
            # Conditions
            "acceptation_conditions": FieldValidationConfig(
                field_type=FieldType.CHECKBOX,
                required=True,
                error_messages={"required": "Vous devez accepter les conditions d'annulation"}
            )
        }


# Instance globale du moteur de validation
validation_engine = FormValidationEngine()