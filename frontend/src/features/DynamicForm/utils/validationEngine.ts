/**
 * Moteur de validation pour les formulaires dynamiques
 * Gère toutes les règles de validation définies dans le référentiel
 */

/* eslint-disable @typescript-eslint/no-explicit-any */
import type { FieldConfig, ValidationRule } from '../types/referentiel.types';

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

/**
 * Valide un champ individuel
 */
export async function validateField(
  field: FieldConfig,
  value: any,
  formValues: Record<string, any> = {},
  customValidators: Record<string, (value: any, formValues: Record<string, any>, field: FieldConfig) => boolean | Promise<boolean>> = {}
): Promise<ValidationResult> {
  const errors: string[] = [];

  // Champ obligatoire
  if (field.required && isEmpty(value)) {
    const message = field.validation?.find(v => v.type === 'required')?.message;
    errors.push(message || `Le champ ${field.label} est obligatoire`);
    return { isValid: false, errors };
  }

  // Si vide et non obligatoire, pas besoin de valider
  if (isEmpty(value)) {
    return { isValid: true, errors: [] };
  }

  // Appliquer les règles de validation
  if (field.validation) {
    for (const rule of field.validation) {
      const result = await validateRule(rule, value, field, formValues, customValidators);
      if (!result.isValid) {
        errors.push(result.message);
      }
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Valide une règle individuelle
 */
async function validateRule(
  rule: ValidationRule,
  value: any,
  field: FieldConfig,
  formValues: Record<string, any>,
  customValidators: Record<string, (value: any, formValues: Record<string, any>, field: FieldConfig) => boolean | Promise<boolean>>
): Promise<{ isValid: boolean; message: string }> {
  switch (rule.type) {
    case 'required':
      return {
        isValid: !isEmpty(value),
        message: rule.message
      };

    case 'email':
      return {
        isValid: validateEmail(value),
        message: rule.message
      };

    case 'url':
      return {
        isValid: validateURL(value),
        message: rule.message
      };

    case 'pattern':
      if (!rule.pattern) {
        return { isValid: true, message: '' };
      }
      return {
        isValid: new RegExp(rule.pattern).test(String(value)),
        message: rule.message
      };

    case 'min':
      if (rule.value === undefined) {
        return { isValid: true, message: '' };
      }
      return {
        isValid: Number(value) >= Number(rule.value),
        message: rule.message
      };

    case 'max':
      if (rule.value === undefined) {
        return { isValid: true, message: '' };
      }
      return {
        isValid: Number(value) <= Number(rule.value),
        message: rule.message
      };

    case 'minLength':
      if (rule.value === undefined) {
        return { isValid: true, message: '' };
      }
      return {
        isValid: String(value).length >= Number(rule.value),
        message: rule.message
      };

    case 'maxLength':
      if (rule.value === undefined) {
        return { isValid: true, message: '' };
      }
      return {
        isValid: String(value).length <= Number(rule.value),
        message: rule.message
      };

    case 'custom': {
      if (!rule.customValidator) {
        return { isValid: true, message: '' };
      }

      const validator = customValidators[rule.customValidator];
      if (!validator || typeof validator !== 'function') {
        console.warn(`Validateur personnalisé introuvable: ${rule.customValidator}`);
        return { isValid: true, message: '' };
      }

      try {
        const result = await validator(value, formValues, field);
        return {
          isValid: Boolean(result),
          message: rule.message
        };
      } catch (error) {
        console.error(`Erreur dans le validateur ${rule.customValidator}:`, error);
        return { isValid: false, message: rule.message };
      }
    }

    case 'dependency': {
      if (!rule.dependsOn) {
        return { isValid: true, message: '' };
      }

      const dependentValue = formValues[rule.dependsOn.field];
      const conditionMet = checkCondition(
        dependentValue,
        rule.dependsOn.condition,
        rule.dependsOn.value
      );

      return {
        isValid: conditionMet,
        message: rule.message
      };
    }

    default:
      console.warn(`Type de validation non supporté: ${rule.type}`);
      return { isValid: true, message: '' };
  }
}

/**
 * Valide tous les champs d'un formulaire
 */
export async function validateForm(
  fields: FieldConfig[],
  values: Record<string, any>,
  customValidators: Record<string, (value: any, formValues: Record<string, any>, field: FieldConfig) => boolean | Promise<boolean>> = {}
): Promise<Record<string, string[]>> {
  const errors: Record<string, string[]> = {};

  for (const field of fields) {
    const value = values[field.id];
    const result = await validateField(field, value, values, customValidators);

    if (!result.isValid) {
      errors[field.id] = result.errors;
    }
  }

  return errors;
}

/**
 * Vérifie si une valeur est vide
 */
function isEmpty(value: any): boolean {
  if (value === null || value === undefined) {
    return true;
  }

  if (typeof value === 'string') {
    return value.trim().length === 0;
  }

  if (Array.isArray(value)) {
    return value.length === 0;
  }

  if (typeof value === 'object') {
    return Object.keys(value).length === 0;
  }

  return false;
}

/**
 * Valide un email
 */
function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Valide une URL
 */
function validateURL(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Vérifie une condition
 */
function checkCondition(
  value: any,
  operator: string,
  expectedValue: any
): boolean {
  switch (operator) {
    case 'equals':
      return value === expectedValue;

    case 'notEquals':
      return value !== expectedValue;

    case 'contains':
      if (typeof value === 'string') {
        return value.includes(String(expectedValue));
      }
      if (Array.isArray(value)) {
        return value.includes(expectedValue);
      }
      return false;

    case 'notContains':
      if (typeof value === 'string') {
        return !value.includes(String(expectedValue));
      }
      if (Array.isArray(value)) {
        return !value.includes(expectedValue);
      }
      return true;

    case 'greaterThan':
      return Number(value) > Number(expectedValue);

    case 'lessThan':
      return Number(value) < Number(expectedValue);

    case 'isEmpty':
      return isEmpty(value);

    case 'isNotEmpty':
      return !isEmpty(value);

    default:
      console.warn(`Opérateur de condition non supporté: ${operator}`);
      return false;
  }
}

/**
 * Évalue une condition d'affichage
 */
export function evaluateDisplayCondition(
  condition: any,
  formValues: Record<string, any>
): boolean {
  if (!condition) {
    return true;
  }

  // Condition simple
  if (condition.field && condition.operator) {
    const fieldValue = formValues[condition.field];
    return checkCondition(fieldValue, condition.operator, condition.value);
  }

  // Conditions imbriquées (AND/OR)
  if (condition.conditions && Array.isArray(condition.conditions)) {
    const logic = condition.logic || 'AND';
    const results = condition.conditions.map((c: any) =>
      evaluateDisplayCondition(c, formValues)
    );

    if (logic === 'AND') {
      return results.every((r: boolean) => r);
    } else if (logic === 'OR') {
      return results.some((r: boolean) => r);
    }
  }

  return true;
}

/**
 * Calcule la valeur d'un champ calculé
 */
export function computeFieldValue(
  formula: string,
  formValues: Record<string, any>,
  dependsOn: string[]
): any {
  try {
    // Créer un contexte sécurisé avec seulement les champs nécessaires
    const context: Record<string, any> = {};
    dependsOn.forEach(fieldId => {
      context[fieldId] = formValues[fieldId];
    });

    // Remplacer les noms de champs par leurs valeurs
    let evaluableFormula = formula;
    dependsOn.forEach(fieldId => {
      const value = formValues[fieldId];
      // Convertir en nombre si possible, sinon en string entre quotes
      const safeValue = typeof value === 'number' ? value :
                        typeof value === 'boolean' ? value :
                        `"${String(value || '').replace(/"/g, '\\"')}"`;
      evaluableFormula = evaluableFormula.replace(
        new RegExp(`\\b${fieldId}\\b`, 'g'),
        String(safeValue)
      );
    });

    // Évaluation sécurisée (limitée aux expressions mathématiques)
    // En production, utiliser un parser d'expression sécurisé comme math.js
    const result = Function(`"use strict"; return (${evaluableFormula})`)();
    return result;
  } catch (error) {
    console.error('Erreur lors du calcul de la formule:', error);
    return null;
  }
}

/**
 * Collecte tous les champs d'un formulaire (sections -> groupes -> champs)
 */
export function collectAllFields(config: any): FieldConfig[] {
  const fields: FieldConfig[] = [];

  if (config.sections) {
    config.sections.forEach((section: any) => {
      if (section.groups) {
        section.groups.forEach((group: any) => {
          if (group.fields) {
            fields.push(...group.fields);
          }
        });
      }
    });
  }

  return fields;
}

/**
 * Charge les validateurs personnalisés depuis le référentiel
 */
export function loadCustomValidators(
  customValidatorsCode: Record<string, string>
): Record<string, (value: any, formValues: Record<string, any>, field: FieldConfig) => boolean | Promise<boolean>> {
  const validators: Record<string, (value: any, formValues: Record<string, any>, field: FieldConfig) => boolean | Promise<boolean>> = {};

  Object.entries(customValidatorsCode).forEach(([name, code]) => {
    try {
      // Évaluer le code de la fonction
      // Note: En production, utiliser un sandbox approprié
      const validatorFn = Function(`"use strict"; return (${code})`)();
      validators[name] = validatorFn;
    } catch (error) {
      console.error(`Erreur lors du chargement du validateur ${name}:`, error);
    }
  });

  return validators;
}

/**
 * Exemple d'utilisation:
 * 
 * // Validation d'un champ
 * const result = await validateField(field, value, formValues, customValidators);
 * if (!result.isValid) {
 *   console.log(result.errors);
 * }
 * 
 * // Validation du formulaire complet
 * const errors = await validateForm(fields, values, customValidators);
 * 
 * // Évaluation d'une condition
 * const isVisible = evaluateDisplayCondition(condition, formValues);
 * 
 * // Calcul d'un champ
 * const computed = computeFieldValue(formula, formValues, dependsOn);
 */
