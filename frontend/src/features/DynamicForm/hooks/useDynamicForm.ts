/**
 * Hook principal pour gérer un formulaire dynamique
 * Gère l'état, la validation, les champs calculés et les conditions
 */

/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback, useMemo } from 'react';
import type { FormReferentiel, FormState, FormActions, FieldConfig } from '../types/referentiel.types';
import {
  validateField,
  validateForm,
  evaluateDisplayCondition,
  computeFieldValue,
  collectAllFields,
  loadCustomValidators
} from '../utils/validationEngine';
import { getDefaultValue } from '../utils/fieldRenderer';

export interface UseDynamicFormOptions {
  referentiel: FormReferentiel;
  initialValues?: Record<string, any>;
  onSubmit?: (values: Record<string, any>) => Promise<void> | void;
  onFieldChange?: (fieldId: string, value: any, allValues: Record<string, any>) => void;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
  autosave?: boolean;
  autosaveKey?: string;
}

export interface UseDynamicFormReturn {
  state: FormState;
  actions: FormActions;
  fields: FieldConfig[];
  visibleFields: Set<string>;
  computedValues: Record<string, any>;
  isFieldVisible: (fieldId: string) => boolean;
  getFieldValue: (fieldId: string) => any;
  getFieldError: (fieldId: string) => string | undefined;
}

export function useDynamicForm(options: UseDynamicFormOptions): UseDynamicFormReturn {
  const {
    referentiel,
    initialValues = {},
    onSubmit,
    onFieldChange,
    validateOnChange = referentiel.config.validateOnChange ?? false,
    // validateOnBlur pourrait être utilisé dans une future implémentation
    // validateOnBlur = referentiel.config.validateOnBlur ?? true,
    autosave = referentiel.config.autosave?.enabled ?? false,
    autosaveKey = referentiel.config.autosave?.key || `form-${referentiel.config.id}`
  } = options;

  // Collecter tous les champs
  const allFields = useMemo(
    () => collectAllFields(referentiel.config),
    [referentiel]
  );

  // Charger les validateurs personnalisés
  const customValidators = useMemo(
    () => loadCustomValidators(referentiel.customValidators || {}),
    [referentiel]
  );

  // Initialiser les valeurs par défaut
  const defaultValues = useMemo(() => {
    const values: Record<string, any> = {};
    allFields.forEach(field => {
      values[field.id] = getDefaultValue(field);
    });
    return values;
  }, [allFields]);

  // État du formulaire
  const [state, setState] = useState<FormState>(() => {
    // Charger depuis localStorage si autosave activé
    let savedValues = {};
    if (autosave) {
      try {
        const saved = localStorage.getItem(autosaveKey);
        if (saved) {
          savedValues = JSON.parse(saved);
        }
      } catch (error) {
        console.error('Erreur lors du chargement des valeurs sauvegardées:', error);
      }
    }

    return {
      values: { ...defaultValues, ...initialValues, ...savedValues },
      errors: {},
      touched: {},
      isValid: false,
      isSubmitting: false,
      isDirty: false
    };
  });

  // Calculer les champs visibles selon les conditions
  const visibleFields = useMemo(() => {
    const visible = new Set<string>();

    referentiel.config.sections.forEach(section => {
      // Vérifier la condition de la section
      const sectionVisible = evaluateDisplayCondition(
        section.displayConditions,
        state.values
      );

      if (!sectionVisible) return;

      section.groups.forEach(group => {
        // Vérifier la condition du groupe
        const groupVisible = evaluateDisplayCondition(
          group.displayConditions,
          state.values
        );

        if (!groupVisible) return;

        group.fields.forEach(field => {
          // Vérifier la condition du champ
          const fieldVisible = evaluateDisplayCondition(
            field.displayConditions,
            state.values
          );

          if (fieldVisible && !field.hidden) {
            visible.add(field.id);
          }
        });
      });
    });

    return visible;
  }, [referentiel, state.values]);

  // Calculer les valeurs des champs calculés
  const computedValues = useMemo(() => {
    const computed: Record<string, any> = {};

    allFields.forEach(field => {
      if (field.computed) {
        const value = computeFieldValue(
          field.computed.formula,
          state.values,
          field.computed.dependsOn
        );
        computed[field.id] = value;
      }
    });

    return computed;
  }, [allFields, state.values]);

  // Mettre à jour les valeurs calculées dans l'état
  useEffect(() => {
    if (Object.keys(computedValues).length > 0) {
      setState(prev => ({
        ...prev,
        values: {
          ...prev.values,
          ...computedValues
        }
      }));
    }
  }, [computedValues]);

  // Autosave
  useEffect(() => {
    if (autosave && state.isDirty) {
      const timeoutId = setTimeout(() => {
        try {
          localStorage.setItem(autosaveKey, JSON.stringify(state.values));
        } catch (error) {
          console.error('Erreur lors de la sauvegarde automatique:', error);
        }
      }, referentiel.config.autosave?.interval || 3000);

      return () => clearTimeout(timeoutId);
    }
  }, [autosave, autosaveKey, state.values, state.isDirty, referentiel]);

  // Actions
  const setValue = useCallback(
    (fieldId: string, value: any) => {
      setState(prev => {
        const newValues = {
          ...prev.values,
          [fieldId]: value
        };

        // Callback
        if (onFieldChange) {
          onFieldChange(fieldId, value, newValues);
        }

        return {
          ...prev,
          values: newValues,
          isDirty: true
        };
      });

      // Validation à la volée
      if (validateOnChange) {
        const field = allFields.find(f => f.id === fieldId);
        if (field) {
          validateField(field, value, state.values, customValidators).then(result => {
            setState(prev => ({
              ...prev,
              errors: {
                ...prev.errors,
                [fieldId]: result.errors
              }
            }));
          });
        }
      }
    },
    [allFields, customValidators, onFieldChange, state.values, validateOnChange]
  );

  const setValues = useCallback((values: Record<string, any>) => {
    setState(prev => ({
      ...prev,
      values: { ...prev.values, ...values },
      isDirty: true
    }));
  }, []);

  const setError = useCallback((fieldId: string, error: string) => {
    setState(prev => ({
      ...prev,
      errors: {
        ...prev.errors,
        [fieldId]: [error]
      }
    }));
  }, []);

  const clearError = useCallback((fieldId: string) => {
    setState(prev => {
      const newErrors = { ...prev.errors };
      delete newErrors[fieldId];
      return {
        ...prev,
        errors: newErrors
      };
    });
  }, []);

  const setTouched = useCallback((fieldId: string, touched: boolean) => {
    setState(prev => ({
      ...prev,
      touched: {
        ...prev.touched,
        [fieldId]: touched
      }
    }));
  }, []);

  const validate = useCallback(
    async (fieldId?: string): Promise<boolean> => {
      if (fieldId) {
        // Valider un seul champ
        const field = allFields.find(f => f.id === fieldId);
        if (!field) return true;

        const result = await validateField(
          field,
          state.values[fieldId],
          state.values,
          customValidators
        );

        setState(prev => ({
          ...prev,
          errors: {
            ...prev.errors,
            [fieldId]: result.errors
          }
        }));

        return result.isValid;
      } else {
        // Valider tout le formulaire
        const errors = await validateForm(
          allFields.filter(f => visibleFields.has(f.id)),
          state.values,
          customValidators
        );

        setState(prev => ({
          ...prev,
          errors,
          isValid: Object.keys(errors).length === 0
        }));

        return Object.keys(errors).length === 0;
      }
    },
    [allFields, customValidators, state.values, visibleFields]
  );

  const submit = useCallback(async () => {
    setState(prev => ({ ...prev, isSubmitting: true }));

    try {
      // Marquer tous les champs visibles comme touchés pour afficher les erreurs
      const allTouched: Record<string, boolean> = {};
      visibleFields.forEach(fieldId => {
        allTouched[fieldId] = true;
      });
      
      setState(prev => ({
        ...prev,
        touched: { ...prev.touched, ...allTouched }
      }));

      // Validation finale
      const isValid = await validate();

      if (!isValid) {
        setState(prev => ({ ...prev, isSubmitting: false }));
        // Scroll vers la première erreur
        setTimeout(() => {
          const firstError = document.querySelector('[data-error="true"]');
          if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }, 100);
        return;
      }

      // Callback de soumission
      if (onSubmit) {
        await onSubmit(state.values);
      }

      // Nettoyer l'autosave
      if (autosave) {
        try {
          localStorage.removeItem(autosaveKey);
        } catch (error) {
          console.error('Erreur lors du nettoyage de l\'autosave:', error);
        }
      }

      setState(prev => ({
        ...prev,
        isSubmitting: false,
        isDirty: false
      }));
    } catch (error) {
      console.error('Erreur lors de la soumission:', error);
      setState(prev => ({ ...prev, isSubmitting: false }));
      throw error;
    }
  }, [autosave, autosaveKey, onSubmit, state.values, validate]);

  const reset = useCallback(() => {
    setState({
      values: { ...defaultValues, ...initialValues },
      errors: {},
      touched: {},
      isValid: false,
      isSubmitting: false,
      isDirty: false
    });

    // Nettoyer l'autosave
    if (autosave) {
      try {
        localStorage.removeItem(autosaveKey);
      } catch (error) {
        console.error('Erreur lors du nettoyage de l\'autosave:', error);
      }
    }
  }, [autosave, autosaveKey, defaultValues, initialValues]);

  // Fonctions utilitaires
  const isFieldVisible = useCallback(
    (fieldId: string) => visibleFields.has(fieldId),
    [visibleFields]
  );

  const getFieldValue = useCallback(
    (fieldId: string) => state.values[fieldId],
    [state.values]
  );

  const getFieldError = useCallback(
    (fieldId: string) => {
      const errors = state.errors[fieldId];
      return errors && errors.length > 0 ? errors[0] : undefined;
    },
    [state.errors]
  );

  // Note: handleBlur pourrait être ajouté ici pour une validation onBlur
  // Pour l'instant, la validation se fait onChange ou sur submit

  return {
    state,
    actions: {
      setValue,
      setValues,
      setError,
      clearError,
      setTouched,
      validate,
      submit,
      reset
    },
    fields: allFields,
    visibleFields,
    computedValues,
    isFieldVisible,
    getFieldValue,
    getFieldError
  };
}
