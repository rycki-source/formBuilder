/**
 * Index principal pour le module de formulaires dynamiques
 * Exporte tous les composants, hooks, types et utilitaires
 */

// Types
export type {
  FieldType,
  LayoutType,
  ValidationType,
  ValidationRule,
  DisplayCondition,
  FieldOption,
  FieldConfig,
  FieldGroup,
  FormSection,
  FormConfig,
  FormReferentiel,
  FormState,
  FormActions,
  ImportSource,
  ImportResult,
  ImportOptions
} from './types/referentiel.types';

// Composants
export { default as DynamicForm } from './components/DynamicForm';
export type { DynamicFormProps } from './components/DynamicForm';

export { default as DynamicField } from './components/DynamicField';
export type { DynamicFieldProps } from './components/DynamicField';

export { default as FormImporter } from './components/FormImporter';
export type { FormImporterProps } from './components/FormImporter';

// Hooks
export { useDynamicForm } from './hooks/useDynamicForm';
export type { UseDynamicFormOptions, UseDynamicFormReturn } from './hooks/useDynamicForm';

// Utilitaires
export {
  validateReferentiel,
  type ValidationError,
  type ValidationResult
} from './utils/referentielValidator';

export {
  parseReferentiel,
  parseFile,
  parseFromURL,
  detectFormat,
  isValidReferentiel,
  stringifyReferentiel,
  toYAML,
  type SupportedFormat,
  type ParseResult
} from './utils/parser';

export {
  renderField,
  getDefaultValue,
  formatFieldValue,
  type FieldRendererProps
} from './utils/fieldRenderer';

export {
  validateField,
  validateForm,
  evaluateDisplayCondition,
  computeFieldValue,
  collectAllFields,
  loadCustomValidators,
  type ValidationResult as FieldValidationResult
} from './utils/validationEngine';
