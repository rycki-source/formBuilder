/**
 * Utilitaire pour convertir ChampFormulaire en FieldConfig avec validation
 */

import type { ChampFormulaire, ValidationRule } from '../types';
import type { FieldConfig, ValidationRule as DynamicValidationRule } from '../features/DynamicForm/types/referentiel.types';

/**
 * Convertit un ChampFormulaire en FieldConfig avec les règles de validation
 */
export function convertChampToFieldConfig(champ: ChampFormulaire): FieldConfig {
  const fieldConfig: FieldConfig = {
    id: champ.id || `field_${champ.ordre}`,
    name: champ.id || `field_${champ.ordre}`,
    label: champ.label,
    type: mapTypeChampToFieldType(champ.type_champ),
    required: champ.obligatoire,
    placeholder: champ.placeholder,
    validation: [],
  };

  // Ajouter les options pour select/radio
  if (champ.options && (champ.type_champ === 'select' || champ.type_champ === 'radio')) {
    fieldConfig.options = champ.options.map((opt) => ({
      value: opt,
      label: opt,
    }));
  }

  // Convertir les règles de validation personnalisées
  if (champ.validation_rules && Array.isArray(champ.validation_rules)) {
    fieldConfig.validation = champ.validation_rules.map(rule => 
      convertValidationRule(rule)
    );
  }

  // Ajouter la règle "required" si le champ est obligatoire
  if (champ.obligatoire && !fieldConfig.validation?.some(v => v.type === 'required')) {
    fieldConfig.validation = fieldConfig.validation || [];
    fieldConfig.validation.unshift({
      type: 'required',
      message: `Le champ ${champ.label} est obligatoire`,
    });
  }

  return fieldConfig;
}

/**
 * Convertit les types de champs du backend vers les types DynamicForm
 */
function mapTypeChampToFieldType(typeChamp: ChampFormulaire['type_champ']): FieldConfig['type'] {
  const typeMap: Record<string, FieldConfig['type']> = {
    'text': 'text',
    'email': 'email',
    'number': 'number',
    'date': 'date',
    'select': 'select',
    'textarea': 'textarea',
    'checkbox': 'checkbox',
    'radio': 'radio',
    'file': 'file',
    'button': 'text', // Pas de type button dans FieldConfig
    'geolocation': 'text',
    'signature': 'text',
  };

  return typeMap[typeChamp] || 'text';
}

/**
 * Convertit une ValidationRule en DynamicValidationRule
 */
function convertValidationRule(
  rule: ValidationRule
): DynamicValidationRule {
  const dynamicRule: DynamicValidationRule = {
    type: rule.type,
    message: rule.message.replace('{value}', String(rule.value || '')),
  };

  // Ajouter les propriétés spécifiques selon le type
  switch (rule.type) {
    case 'minLength':
    case 'maxLength':
    case 'min':
    case 'max':
      if (rule.value !== undefined) {
        dynamicRule.value = rule.value;
      }
      break;

    case 'pattern':
      if (rule.pattern) {
        dynamicRule.pattern = rule.pattern;
      }
      break;

    case 'custom':
      if (rule.customValidator) {
        dynamicRule.customValidator = rule.customValidator;
      }
      break;

    case 'dependency':
      if (rule.dependsOn) {
        dynamicRule.dependsOn = rule.dependsOn;
      }
      break;
  }

  return dynamicRule;
}

/**
 * Convertit un tableau de ChampFormulaire en tableau de FieldConfig
 */
export function convertChampsToFieldConfigs(champs: ChampFormulaire[]): FieldConfig[] {
  return champs
    .sort((a, b) => a.ordre - b.ordre)
    .map(champ => convertChampToFieldConfig(champ));
}
