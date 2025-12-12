/**
 * Types TypeScript pour le référentiel de formulaire dynamique
 * 
 * Ce fichier définit la structure complète d'un référentiel de configuration
 * permettant de générer dynamiquement des formulaires complexes.
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

// ============================================================================
// TYPES DE BASE
// ============================================================================

/**
 * Types de champs supportés
 */
export type FieldType =
  | 'text'
  | 'textarea'
  | 'number'
  | 'email'
  | 'password'
  | 'tel'
  | 'url'
  | 'date'
  | 'datetime-local'
  | 'time'
  | 'month'
  | 'week'
  | 'select'
  | 'multiselect'
  | 'radio'
  | 'checkbox'
  | 'switch'
  | 'file'
  | 'color'
  | 'range'
  | 'hidden'
  | 'custom';

/**
 * Types de layout/disposition
 */
export type LayoutType =
  | 'grid'
  | 'flex'
  | 'tabs'
  | 'accordion'
  | 'stepper'
  | 'columns';

/**
 * Types de validation
 */
export type ValidationType =
  | 'required'
  | 'email'
  | 'url'
  | 'pattern'
  | 'min'
  | 'max'
  | 'minLength'
  | 'maxLength'
  | 'custom'
  | 'dependency';

// ============================================================================
// RÈGLES DE VALIDATION
// ============================================================================

export interface ValidationRule {
  type: ValidationType;
  message: string;
  value?: string | number | boolean;
  pattern?: string;
  customValidator?: string; // Nom de la fonction de validation
  dependsOn?: {
    field: string;
    condition: 'equals' | 'notEquals' | 'contains' | 'greaterThan' | 'lessThan';
    value: any;
  };
}

// ============================================================================
// CONDITIONS D'AFFICHAGE
// ============================================================================

export interface DisplayCondition {
  field: string;
  operator: 'equals' | 'notEquals' | 'contains' | 'notContains' | 'greaterThan' | 'lessThan' | 'isEmpty' | 'isNotEmpty';
  value?: any;
  logic?: 'AND' | 'OR';
  conditions?: DisplayCondition[]; // Pour les conditions imbriquées
}

// ============================================================================
// OPTIONS POUR LES CHAMPS SELECT/RADIO
// ============================================================================

export interface FieldOption {
  label: string;
  value: string | number;
  disabled?: boolean;
  icon?: string;
  description?: string;
  group?: string; // Pour grouper les options
}

// ============================================================================
// CONFIGURATION DES CHAMPS
// ============================================================================

export interface FieldConfig {
  // Identification
  id: string;
  name: string;
  type: FieldType;

  // Affichage
  label: string;
  placeholder?: string;
  tooltip?: string;
  description?: string;
  icon?: string;

  // Valeurs
  defaultValue?: any;
  value?: any;
  options?: FieldOption[]; // Pour select, radio, checkbox
  
  // Comportement
  required?: boolean;
  disabled?: boolean;
  readonly?: boolean;
  hidden?: boolean;
  
  // Validation
  validation?: ValidationRule[];
  
  // Conditions
  displayConditions?: DisplayCondition;
  
  // Champs calculés
  computed?: {
    formula: string; // Expression à évaluer
    dependsOn: string[]; // Champs dont dépend le calcul
  };
  
  // Apparence
  className?: string;
  style?: Record<string, string>;
  width?: string | number; // Pour le layout grid
  span?: number; // Nombre de colonnes occupées
  
  // Spécifique aux fichiers
  accept?: string; // Types de fichiers acceptés
  multiple?: boolean;
  maxSize?: number; // En bytes
  
  // Spécifique aux nombres
  min?: number;
  max?: number;
  step?: number;
  
  // Spécifique au texte
  minLength?: number;
  maxLength?: number;
  rows?: number; // Pour textarea
  
  // Composant personnalisé
  customComponent?: string; // Nom du composant custom
  customProps?: Record<string, any>;
}

// ============================================================================
// SECTIONS ET GROUPES
// ============================================================================

export interface FieldGroup {
  id: string;
  title?: string;
  description?: string;
  fields: FieldConfig[];
  layout?: LayoutType;
  columns?: number; // Pour grid layout
  className?: string;
  collapsible?: boolean;
  collapsed?: boolean;
  displayConditions?: DisplayCondition;
}

export interface FormSection {
  id: string;
  title: string;
  description?: string;
  icon?: string;
  groups: FieldGroup[];
  order?: number;
  displayConditions?: DisplayCondition;
}

// ============================================================================
// CONFIGURATION DU FORMULAIRE
// ============================================================================

export interface FormConfig {
  // Métadonnées
  id: string;
  version: string;
  name: string;
  description?: string;
  
  // Structure
  sections: FormSection[];
  
  // Layout global
  layout?: {
    type: LayoutType;
    columns?: number;
    gap?: string;
    responsive?: {
      mobile?: number;
      tablet?: number;
      desktop?: number;
    };
  };
  
  // Comportement
  submitButton?: {
    label?: string;
    icon?: string;
    position?: 'left' | 'center' | 'right';
    disabled?: boolean;
  };
  
  cancelButton?: {
    label?: string;
    show?: boolean;
  };
  
  // Validation globale
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
  validateOnSubmit?: boolean;
  
  // Callbacks (noms de fonctions)
  onSubmit?: string;
  onCancel?: string;
  onFieldChange?: string;
  onValidate?: string;
  
  // Persistance
  autosave?: {
    enabled: boolean;
    interval?: number; // en millisecondes
    key?: string; // Clé localStorage
  };
  
  // Apparence
  theme?: {
    primaryColor?: string;
    errorColor?: string;
    successColor?: string;
    spacing?: string;
  };
  
  // Messages
  messages?: {
    required?: string;
    invalid?: string;
    success?: string;
    error?: string;
  };
}

// ============================================================================
// RÉFÉRENTIEL COMPLET
// ============================================================================

export interface FormReferentiel {
  $schema?: string; // Pour validation JSON Schema
  version: string;
  metadata: {
    name: string;
    description?: string;
    author?: string;
    createdAt?: string;
    updatedAt?: string;
    tags?: string[];
  };
  config: FormConfig;
  customValidators?: Record<string, string>; // Code des validateurs custom
  customComponents?: Record<string, string>; // Code des composants custom
}

// ============================================================================
// TYPES POUR L'ÉTAT DU FORMULAIRE
// ============================================================================

export interface FormState {
  values: Record<string, unknown>;
  errors: Record<string, string[]>;
  touched: Record<string, boolean>;
  isValid: boolean;
  isSubmitting: boolean;
  isDirty: boolean;
}

export interface FormActions {
  setValue: (field: string, value: unknown) => void;
  setValues: (values: Record<string, unknown>) => void;
  setError: (field: string, error: string) => void;
  clearError: (field: string) => void;
  setTouched: (field: string, touched: boolean) => void;
  validate: (field?: string) => Promise<boolean>;
  submit: () => Promise<void>;
  reset: () => void;
}

// ============================================================================
// TYPES POUR L'IMPORT
// ============================================================================

export type ImportSource = 'file' | 'url' | 'paste';

export interface ImportResult {
  success: boolean;
  referentiel?: FormReferentiel;
  errors?: string[];
  warnings?: string[];
}

export interface ImportOptions {
  source: ImportSource;
  content?: string | File;
  url?: string;
  validateSchema?: boolean;
  allowWarnings?: boolean;
}
