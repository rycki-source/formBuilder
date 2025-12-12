"""Schémas Pydantic pour les référentiels de formulaires dynamiques"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime


# ============================================================================
# Schémas pour les métadonnées
# ============================================================================

class ReferentielMetadata(BaseModel):
    """Métadonnées d'un référentiel"""
    name: str
    description: Optional[str] = None
    author: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    tags: List[str] = []


# ============================================================================
# Schémas pour les options de champs
# ============================================================================

class FieldOption(BaseModel):
    """Option pour select/radio/checkbox"""
    label: str
    value: Any
    disabled: Optional[bool] = False
    icon: Optional[str] = None
    description: Optional[str] = None
    group: Optional[str] = None


# ============================================================================
# Schémas pour les règles de validation
# ============================================================================

class ValidationRule(BaseModel):
    """Règle de validation pour un champ"""
    type: Literal[
        "required", "email", "url", "pattern", 
        "min", "max", "minLength", "maxLength",
        "custom", "dependency"
    ]
    message: str
    value: Optional[Any] = None
    pattern: Optional[str] = None
    customValidator: Optional[str] = None
    dependsOn: Optional[Dict[str, Any]] = None


# ============================================================================
# Schémas pour les conditions d'affichage
# ============================================================================

class DisplayCondition(BaseModel):
    """Condition d'affichage d'un élément"""
    field: str
    operator: Literal[
        "equals", "notEquals", "contains", "notContains",
        "greaterThan", "lessThan", "isEmpty", "isNotEmpty"
    ]
    value: Optional[Any] = None
    logic: Optional[Literal["AND", "OR"]] = None
    conditions: Optional[List['DisplayCondition']] = None


# ============================================================================
# Schémas pour les champs
# ============================================================================

class FieldComputed(BaseModel):
    """Configuration pour un champ calculé"""
    formula: str
    dependsOn: List[str]


class FieldConfig(BaseModel):
    """Configuration complète d'un champ"""
    # Identification
    id: str
    name: str
    type: Literal[
        "text", "textarea", "number", "email", "password", "tel", "url",
        "date", "datetime-local", "time", "month", "week",
        "select", "multiselect", "radio", "checkbox", "switch",
        "file", "color", "range", "hidden", "custom"
    ]
    
    # Affichage
    label: str
    placeholder: Optional[str] = None
    tooltip: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    
    # Valeurs
    defaultValue: Optional[Any] = None
    value: Optional[Any] = None
    options: Optional[List[FieldOption]] = None
    
    # Comportement
    required: Optional[bool] = False
    disabled: Optional[bool] = False
    readonly: Optional[bool] = False
    hidden: Optional[bool] = False
    
    # Validation
    validation: Optional[List[ValidationRule]] = None
    
    # Conditions
    displayConditions: Optional[DisplayCondition] = None
    
    # Champs calculés
    computed: Optional[FieldComputed] = None
    
    # Apparence
    className: Optional[str] = None
    style: Optional[Dict[str, str]] = None
    width: Optional[Any] = None
    span: Optional[int] = None
    
    # Spécifique aux fichiers
    accept: Optional[str] = None
    multiple: Optional[bool] = None
    maxSize: Optional[int] = None
    
    # Spécifique aux nombres
    min: Optional[Any] = None
    max: Optional[Any] = None
    step: Optional[Any] = None
    
    # Spécifique au texte
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    rows: Optional[int] = None
    
    # Composant personnalisé
    customComponent: Optional[str] = None
    customProps: Optional[Dict[str, Any]] = None


# ============================================================================
# Schémas pour les groupes et sections
# ============================================================================

class FieldGroup(BaseModel):
    """Groupe de champs"""
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    fields: List[FieldConfig]
    layout: Optional[Literal["grid", "flex", "tabs", "accordion", "stepper", "columns"]] = "grid"
    columns: Optional[int] = 1
    className: Optional[str] = None
    collapsible: Optional[bool] = False
    collapsed: Optional[bool] = False
    displayConditions: Optional[DisplayCondition] = None


class FormSection(BaseModel):
    """Section de formulaire"""
    id: str
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    groups: List[FieldGroup]
    order: Optional[int] = 0
    displayConditions: Optional[DisplayCondition] = None


# ============================================================================
# Schémas pour la configuration globale
# ============================================================================

class FormLayoutConfig(BaseModel):
    """Configuration du layout global"""
    type: Optional[Literal["grid", "flex", "tabs", "accordion", "stepper", "columns"]] = "grid"
    columns: Optional[int] = 1
    gap: Optional[str] = None
    responsive: Optional[Dict[str, int]] = None


class FormButtonConfig(BaseModel):
    """Configuration d'un bouton"""
    label: Optional[str] = None
    icon: Optional[str] = None
    position: Optional[Literal["left", "center", "right"]] = "center"
    disabled: Optional[bool] = False
    show: Optional[bool] = True


class FormAutosaveConfig(BaseModel):
    """Configuration de la sauvegarde automatique"""
    enabled: bool
    interval: Optional[int] = 30000
    key: Optional[str] = None


class FormThemeConfig(BaseModel):
    """Configuration du thème"""
    primaryColor: Optional[str] = None
    errorColor: Optional[str] = None
    successColor: Optional[str] = None
    spacing: Optional[str] = None


class FormMessagesConfig(BaseModel):
    """Messages personnalisés"""
    required: Optional[str] = None
    invalid: Optional[str] = None
    success: Optional[str] = None
    error: Optional[str] = None


class FormConfig(BaseModel):
    """Configuration complète du formulaire"""
    id: str
    version: str
    name: str
    description: Optional[str] = None
    
    sections: List[FormSection]
    
    layout: Optional[FormLayoutConfig] = None
    submitButton: Optional[FormButtonConfig] = None
    cancelButton: Optional[FormButtonConfig] = None
    
    validateOnChange: Optional[bool] = False
    validateOnBlur: Optional[bool] = True
    validateOnSubmit: Optional[bool] = True
    
    onSubmit: Optional[str] = None
    onCancel: Optional[str] = None
    onFieldChange: Optional[str] = None
    onValidate: Optional[str] = None
    
    autosave: Optional[FormAutosaveConfig] = None
    theme: Optional[FormThemeConfig] = None
    messages: Optional[FormMessagesConfig] = None


# ============================================================================
# Schéma principal du référentiel
# ============================================================================

class ReferentielBase(BaseModel):
    """Schéma de base pour un référentiel"""
    version: str = "1.0.0"
    metadata: ReferentielMetadata
    config: FormConfig
    customValidators: Optional[Dict[str, str]] = None
    customComponents: Optional[Dict[str, str]] = None


class ReferentielCreate(ReferentielBase):
    """Schéma pour créer un référentiel"""
    source_type: Literal["excel", "json", "yaml", "import", "manual"] = "manual"
    source_file: Optional[str] = None
    is_template: Optional[bool] = False


class ReferentielUpdate(BaseModel):
    """Schéma pour mettre à jour un référentiel"""
    metadata: Optional[ReferentielMetadata] = None
    config: Optional[FormConfig] = None
    customValidators: Optional[Dict[str, str]] = None
    customComponents: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None
    is_template: Optional[bool] = None
    valide: Optional[bool] = None


class ReferentielInDB(ReferentielBase):
    """Schéma pour un référentiel en base de données"""
    id: int
    ref_id: Optional[str] = None
    source_type: str
    source_file: Optional[str] = None
    is_active: bool
    is_template: bool
    valide: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReferentielResponse(BaseModel):
    """Réponse API pour un référentiel"""
    id: int
    ref_id: Optional[str] = None
    version: str
    metadata: ReferentielMetadata
    config: FormConfig
    custom_validators: Optional[Dict[str, str]] = None
    custom_components: Optional[Dict[str, str]] = None
    source_type: str
    source_file: Optional[str] = None
    is_active: bool
    is_template: bool
    valide: bool
    created_at: str
    updated_at: Optional[str] = None
    personne_import_id: int


class ReferentielList(BaseModel):
    """Liste de référentiels"""
    items: List[ReferentielResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Schémas pour l'import
# ============================================================================

class ReferentielImportRequest(BaseModel):
    """Requête d'import de référentiel"""
    source_type: Literal["excel", "json", "yaml"]
    content: Optional[str] = None  # Contenu texte pour JSON/YAML
    url: Optional[str] = None  # URL pour récupération distante
    validate_schema: Optional[bool] = True
    save_as_template: Optional[bool] = False


class ReferentielImportResponse(BaseModel):
    """Réponse d'import de référentiel"""
    success: bool
    message: Optional[str] = None
    referentiel: Optional[ReferentielResponse] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


# Mise à jour des références cycliques
DisplayCondition.model_rebuild()
