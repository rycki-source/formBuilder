/**
 * Validateur de référentiel de formulaire
 * 
 * Valide la structure et le contenu d'un référentiel avant son utilisation
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

export interface ValidationError {
  path: string;
  message: string;
  severity: 'error' | 'warning';
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
}

/**
 * Valider un référentiel complet
 */
export function validateReferentiel(referentiel: any): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  // Validation de la structure de base
  if (!referentiel || typeof referentiel !== 'object') {
    errors.push({
      path: 'root',
      message: 'Le référentiel est vide ou invalide',
      severity: 'error'
    });
    return { isValid: false, errors, warnings };
  }

  // Validation de la version
  if (!referentiel.version) {
    errors.push({
      path: 'version',
      message: 'La version est obligatoire',
      severity: 'error'
    });
  }

  // Validation des métadonnées
  if (!referentiel.metadata) {
    errors.push({
      path: 'metadata',
      message: 'Les métadonnées sont obligatoires',
      severity: 'error'
    });
  } else {
    if (!referentiel.metadata.name) {
      errors.push({
        path: 'metadata.name',
        message: 'Le nom du formulaire est obligatoire',
        severity: 'error'
      });
    }
  }

  // Validation de la configuration
  if (!referentiel.config) {
    errors.push({
      path: 'config',
      message: 'La configuration est obligatoire',
      severity: 'error'
    });
    return { isValid: false, errors, warnings };
  }

  const config = referentiel.config;

  // Validation des sections
  if (!config.sections || !Array.isArray(config.sections)) {
    errors.push({
      path: 'config.sections',
      message: 'Les sections sont obligatoires et doivent être un tableau',
      severity: 'error'
    });
  } else {
    if (config.sections.length === 0) {
      warnings.push({
        path: 'config.sections',
        message: 'Le formulaire ne contient aucune section',
        severity: 'warning'
      });
    }

    // Validation de chaque section
    config.sections.forEach((section: any, sectionIndex: number) => {
      validateSection(section, `config.sections[${sectionIndex}]`, errors, warnings);
    });
  }

  // Validation des IDs uniques
  validateUniqueIds(config, errors);

  // Validation des dépendances de champs
  validateFieldDependencies(config, errors);

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Valide une section
 */
function validateSection(
  section: any,
  path: string,
  errors: ValidationError[],
  warnings: ValidationError[]
): void {
  if (!section.id) {
    errors.push({
      path: `${path}.id`,
      message: 'L\'ID de la section est obligatoire',
      severity: 'error'
    });
  }

  if (!section.title) {
    warnings.push({
      path: `${path}.title`,
      message: 'Le titre de la section est recommandé',
      severity: 'warning'
    });
  }

  if (!section.groups || !Array.isArray(section.groups)) {
    errors.push({
      path: `${path}.groups`,
      message: 'Les groupes de champs sont obligatoires',
      severity: 'error'
    });
  } else {
    if (section.groups.length === 0) {
      warnings.push({
        path: `${path}.groups`,
        message: 'La section ne contient aucun groupe',
        severity: 'warning'
      });
    }

    section.groups.forEach((group: any, groupIndex: number) => {
      validateGroup(group, `${path}.groups[${groupIndex}]`, errors, warnings);
    });
  }

  // Validation des conditions d'affichage
  if (section.displayConditions) {
    validateDisplayConditions(
      section.displayConditions,
      `${path}.displayConditions`,
      errors
    );
  }
}

/**
 * Valide un groupe de champs
 */
function validateGroup(
  group: any,
  path: string,
  errors: ValidationError[],
  warnings: ValidationError[]
): void {
  if (!group.id) {
    errors.push({
      path: `${path}.id`,
      message: 'L\'ID du groupe est obligatoire',
      severity: 'error'
    });
  }

  if (!group.fields || !Array.isArray(group.fields)) {
    errors.push({
      path: `${path}.fields`,
      message: 'Les champs sont obligatoires',
      severity: 'error'
    });
  } else {
    if (group.fields.length === 0) {
      warnings.push({
        path: `${path}.fields`,
        message: 'Le groupe ne contient aucun champ',
        severity: 'warning'
      });
    }

    group.fields.forEach((field: any, fieldIndex: number) => {
      validateField(field, `${path}.fields[${fieldIndex}]`, errors, warnings);
    });
  }

  // Validation du layout
  if (group.layout === 'grid' && group.columns) {
    if (group.columns < 1 || group.columns > 12) {
      warnings.push({
        path: `${path}.columns`,
        message: 'Le nombre de colonnes devrait être entre 1 et 12',
        severity: 'warning'
      });
    }
  }
}

/**
 * Valide un champ
 */
function validateField(
  field: any,
  path: string,
  errors: ValidationError[],
  warnings: ValidationError[]
): void {
  // Validation des propriétés obligatoires
  if (!field.id) {
    errors.push({
      path: `${path}.id`,
      message: 'L\'ID du champ est obligatoire',
      severity: 'error'
    });
  }

  if (!field.name) {
    errors.push({
      path: `${path}.name`,
      message: 'Le nom du champ est obligatoire',
      severity: 'error'
    });
  }

  if (!field.type) {
    errors.push({
      path: `${path}.type`,
      message: 'Le type du champ est obligatoire',
      severity: 'error'
    });
  } else {
    // Validation du type
    const validTypes = [
      'text', 'textarea', 'number', 'email', 'password', 'tel', 'url',
      'date', 'datetime-local', 'time', 'month', 'week',
      'select', 'multiselect', 'radio', 'checkbox', 'switch',
      'file', 'color', 'range', 'hidden', 'custom'
    ];

    if (!validTypes.includes(field.type)) {
      errors.push({
        path: `${path}.type`,
        message: `Type de champ invalide: ${field.type}`,
        severity: 'error'
      });
    }

    // Validation des options pour select/radio/checkbox
    if (['select', 'multiselect', 'radio'].includes(field.type)) {
      if (!field.options || !Array.isArray(field.options)) {
        errors.push({
          path: `${path}.options`,
          message: `Le champ de type ${field.type} doit avoir des options`,
          severity: 'error'
        });
      } else if (field.options.length === 0) {
        warnings.push({
          path: `${path}.options`,
          message: 'Le champ ne contient aucune option',
          severity: 'warning'
        });
      }
    }

    // Validation des champs de fichier
    if (field.type === 'file') {
      if (field.maxSize && field.maxSize > 104857600) { // 100MB
        warnings.push({
          path: `${path}.maxSize`,
          message: 'La taille maximale du fichier est très élevée (> 100MB)',
          severity: 'warning'
        });
      }
    }

    // Validation des champs numériques
    if (field.type === 'number' || field.type === 'range') {
      if (field.min !== undefined && field.max !== undefined && field.min > field.max) {
        errors.push({
          path: `${path}`,
          message: 'La valeur minimale ne peut pas être supérieure à la valeur maximale',
          severity: 'error'
        });
      }
    }
  }

  if (!field.label) {
    warnings.push({
      path: `${path}.label`,
      message: 'Le label du champ est recommandé',
      severity: 'warning'
    });
  }

  // Validation des règles de validation
  if (field.validation && Array.isArray(field.validation)) {
    field.validation.forEach((rule: any, ruleIndex: number) => {
      validateValidationRule(rule, `${path}.validation[${ruleIndex}]`, errors);
    });
  }

  // Validation des conditions d'affichage
  if (field.displayConditions) {
    validateDisplayConditions(field.displayConditions, `${path}.displayConditions`, errors);
  }

  // Validation des champs calculés
  if (field.computed) {
    if (!field.computed.formula) {
      errors.push({
        path: `${path}.computed.formula`,
        message: 'La formule de calcul est obligatoire',
        severity: 'error'
      });
    }

    if (!field.computed.dependsOn || !Array.isArray(field.computed.dependsOn)) {
      errors.push({
        path: `${path}.computed.dependsOn`,
        message: 'Les dépendances du champ calculé sont obligatoires',
        severity: 'error'
      });
    }

    if (field.computed.dependsOn?.length === 0) {
      warnings.push({
        path: `${path}.computed.dependsOn`,
        message: 'Le champ calculé n\'a aucune dépendance',
        severity: 'warning'
      });
    }
  }
}

/**
 * Valide une règle de validation
 */
function validateValidationRule(
  rule: any,
  path: string,
  errors: ValidationError[]
): void {
  if (!rule.type) {
    errors.push({
      path: `${path}.type`,
      message: 'Le type de validation est obligatoire',
      severity: 'error'
    });
  }

  if (!rule.message) {
    errors.push({
      path: `${path}.message`,
      message: 'Le message de validation est obligatoire',
      severity: 'error'
    });
  }

  // Validation spécifique selon le type
  switch (rule.type) {
    case 'pattern':
      if (!rule.pattern) {
        errors.push({
          path: `${path}.pattern`,
          message: 'Le pattern est obligatoire pour la validation de type "pattern"',
          severity: 'error'
        });
      } else {
        try {
          new RegExp(rule.pattern);
        } catch {
          errors.push({
            path: `${path}.pattern`,
            message: 'Le pattern regex est invalide',
            severity: 'error'
          });
        }
      }
      break;

    case 'min':
    case 'max':
    case 'minLength':
    case 'maxLength':
      if (rule.value === undefined) {
        errors.push({
          path: `${path}.value`,
          message: `La valeur est obligatoire pour la validation de type "${rule.type}"`,
          severity: 'error'
        });
      }
      break;

    case 'custom':
      if (!rule.customValidator) {
        errors.push({
          path: `${path}.customValidator`,
          message: 'Le nom du validateur personnalisé est obligatoire',
          severity: 'error'
        });
      }
      break;

    case 'dependency':
      if (!rule.dependsOn) {
        errors.push({
          path: `${path}.dependsOn`,
          message: 'Les dépendances sont obligatoires pour la validation de type "dependency"',
          severity: 'error'
        });
      }
      break;
  }
}

/**
 * Valide des conditions d'affichage
 */
function validateDisplayConditions(
  condition: any,
  path: string,
  errors: ValidationError[]
): void {
  if (!condition.field) {
    errors.push({
      path: `${path}.field`,
      message: 'Le champ de référence est obligatoire',
      severity: 'error'
    });
  }

  if (!condition.operator) {
    errors.push({
      path: `${path}.operator`,
      message: 'L\'opérateur de condition est obligatoire',
      severity: 'error'
    });
  }

  const validOperators = [
    'equals', 'notEquals', 'contains', 'notContains',
    'greaterThan', 'lessThan', 'isEmpty', 'isNotEmpty'
  ];

  if (condition.operator && !validOperators.includes(condition.operator)) {
    errors.push({
      path: `${path}.operator`,
      message: `Opérateur invalide: ${condition.operator}`,
      severity: 'error'
    });
  }

  // Validation des conditions imbriquées
  if (condition.conditions && Array.isArray(condition.conditions)) {
    condition.conditions.forEach((subCondition: any, index: number) => {
      validateDisplayConditions(subCondition, `${path}.conditions[${index}]`, errors);
    });
  }
}

/**
 * Valide l'unicité des IDs
 */
function validateUniqueIds(config: any, errors: ValidationError[]): void {
  const ids = new Set<string>();
  const duplicates = new Set<string>();

  function collectIds(obj: any, path: string) {
    if (obj.id) {
      if (ids.has(obj.id)) {
        duplicates.add(obj.id);
      }
      ids.add(obj.id);
    }

    if (obj.sections) {
      obj.sections.forEach((section: any) => collectIds(section, path));
    }

    if (obj.groups) {
      obj.groups.forEach((group: any) => collectIds(group, path));
    }

    if (obj.fields) {
      obj.fields.forEach((field: any) => collectIds(field, path));
    }
  }

  collectIds(config, 'config');

  duplicates.forEach(id => {
    errors.push({
      path: 'config',
      message: `ID dupliqué trouvé: ${id}`,
      severity: 'error'
    });
  });
}

/**
 * Valide que toutes les dépendances de champs existent
 */
function validateFieldDependencies(config: any, errors: ValidationError[]): void {
  const fieldIds = new Set<string>();

  // Collecter tous les IDs de champs
  function collectFieldIds(obj: any) {
    if (obj.sections) {
      obj.sections.forEach((section: any) => collectFieldIds(section));
    }
    if (obj.groups) {
      obj.groups.forEach((group: any) => collectFieldIds(group));
    }
    if (obj.fields) {
      obj.fields.forEach((field: any) => {
        if (field.id) fieldIds.add(field.id);
      });
    }
  }

  collectFieldIds(config);

  // Vérifier les dépendances
  function checkDependencies(obj: any, path: string) {
    if (obj.displayConditions?.field && !fieldIds.has(obj.displayConditions.field)) {
      errors.push({
        path: `${path}.displayConditions.field`,
        message: `Champ de référence introuvable: ${obj.displayConditions.field}`,
        severity: 'error'
      });
    }

    if (obj.computed?.dependsOn) {
      obj.computed.dependsOn.forEach((dep: string) => {
        if (!fieldIds.has(dep)) {
          errors.push({
            path: `${path}.computed.dependsOn`,
            message: `Champ de dépendance introuvable: ${dep}`,
            severity: 'error'
          });
        }
      });
    }

    if (obj.sections) {
      obj.sections.forEach((section: any, i: number) =>
        checkDependencies(section, `${path}.sections[${i}]`)
      );
    }
    if (obj.groups) {
      obj.groups.forEach((group: any, i: number) =>
        checkDependencies(group, `${path}.groups[${i}]`)
      );
    }
    if (obj.fields) {
      obj.fields.forEach((field: any, i: number) =>
        checkDependencies(field, `${path}.fields[${i}]`)
      );
    }
  }

  checkDependencies(config, 'config');
}
