/**
 * Composant principal pour rendre un formulaire dynamique
 */

/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';
import type { FormReferentiel } from '../types/referentiel.types';
import { useDynamicForm, type UseDynamicFormOptions } from '../hooks/useDynamicForm';
import DynamicField from './DynamicField';
import { Button } from '../../../components/Button';

export interface DynamicFormProps extends Omit<UseDynamicFormOptions, 'referentiel'> {
  referentiel: FormReferentiel;
  className?: string;
  showSubmitButton?: boolean;
  showCancelButton?: boolean;
  submitLabel?: string;
  cancelLabel?: string;
  onCancel?: () => void;
}

const DynamicForm: React.FC<DynamicFormProps> = ({
  referentiel,
  className = '',
  showSubmitButton = true,
  showCancelButton = true,
  submitLabel,
  cancelLabel,
  onCancel,
  ...options
}) => {
  // DEBUG: Log du référentiel reçu
  console.log('🎨 DynamicForm render avec référentiel:', referentiel);
  console.log('🎨 Config:', referentiel?.config);
  console.log('🎨 Sections:', referentiel?.config?.sections);
  console.log('🎨 Nombre de sections:', referentiel?.config?.sections?.length || 0);
  
  const {
    state,
    actions,
    isFieldVisible,
    getFieldValue,
    getFieldError
  } = useDynamicForm({ referentiel, ...options });

  const config = referentiel.config;

  // Labels des boutons
  const finalSubmitLabel = submitLabel || config.submitButton?.label || 'Soumettre';
  const finalCancelLabel = cancelLabel || config.cancelButton?.label || 'Annuler';
  const showCancel = showCancelButton && (config.cancelButton?.show ?? true);

  // Handler pour la soumission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await actions.submit();
  };

  // Handler pour l'annulation
  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      actions.reset();
    }
  };

  // Rendu d'un groupe de champs
  const renderGroup = (group: any) => {
    // Vérifier si le groupe est visible
    const groupFields = group.fields.filter((field: any) =>
      isFieldVisible(field.id)
    );

    if (groupFields.length === 0) return null;

    // Classes de layout
    const layoutClass = group.layout === 'grid'
      ? `grid gap-4`
      : group.layout === 'flex'
      ? `flex flex-wrap gap-4`
      : 'space-y-4';

    const columnsClass = group.columns
      ? `grid-cols-1 md:grid-cols-${group.columns}`
      : '';

    return (
      <div
        key={group.id}
        className={`${group.className || ''} ${
          group.collapsible ? 'border rounded-lg p-4' : ''
        }`}
      >
        {/* Titre du groupe */}
        {group.title && (
          <h3 className="text-lg font-semibold mb-3">{group.title}</h3>
        )}

        {/* Champs du groupe */}
        <div className={`${layoutClass} ${columnsClass}`}>
          {groupFields.map((field: any) => (
            <DynamicField
              key={field.id}
              field={field}
              value={getFieldValue(field.id)}
              error={getFieldError(field.id)}
              touched={state.touched[field.id]}
              disabled={state.isSubmitting}
              onChange={(value) => actions.setValue(field.id, value)}
              onBlur={() => actions.setTouched(field.id, true)}
            />
          ))}
        </div>
      </div>
    );
  };

  // Rendu d'une section
  const renderSection = (section: any) => {
    console.log('📋 renderSection pour:', section.id, section);
    console.log('📋 section.groups:', section.groups);
    
    // Vérifier si la section a des groupes visibles
    const hasVisibleGroups = section.groups.some((group: any) => {
      console.log('📋 Vérification groupe:', group.id, 'fields:', group.fields);
      return group.fields.some((field: any) => {
        const visible = isFieldVisible(field.id);
        console.log('📋 Champ', field.id, 'visible?', visible);
        return visible;
      });
    });

    console.log('📋 hasVisibleGroups:', hasVisibleGroups);
    if (!hasVisibleGroups) {
      console.log('⚠️ Section masquée car aucun groupe visible !');
      return null;
    }

    return (
      <div key={section.id} className="space-y-6">
        {/* En-tête de section */}
        <div className="border-b pb-3">
          <div className="flex items-center gap-3">
            {section.icon && <span className="text-2xl">{section.icon}</span>}
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                {section.title}
              </h2>
              {section.description && (
                <p className="text-sm text-gray-600 mt-1">
                  {section.description}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Groupes de la section */}
        <div className="space-y-6">
          {section.groups.map((group: any) => renderGroup(group))}
        </div>
      </div>
    );
  };

  // Layout global
  const layoutClass = config.layout?.type === 'grid'
    ? 'grid gap-8'
    : config.layout?.type === 'flex'
    ? 'flex flex-col gap-8'
    : 'space-y-8';

  const columnsClass = config.layout?.columns
    ? `grid-cols-1 lg:grid-cols-${config.layout.columns}`
    : '';

  // Position du bouton submit
  const submitButtonPosition = config.submitButton?.position || 'center';
  const buttonPositionClass =
    submitButtonPosition === 'left'
      ? 'justify-start'
      : submitButtonPosition === 'right'
      ? 'justify-end'
      : 'justify-center';

  return (
    <form
      onSubmit={handleSubmit}
      className={`max-w-6xl mx-auto p-6 bg-white rounded-lg shadow-md ${className}`}
      style={config.theme ? {
        '--primary-color': config.theme.primaryColor,
        '--error-color': config.theme.errorColor,
        '--success-color': config.theme.successColor
      } as React.CSSProperties : undefined}
    >
      {/* Titre et description du formulaire */}
      {config.name && (
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{config.name}</h1>
          {config.description && (
            <p className="text-gray-600 mt-2">{config.description}</p>
          )}
        </div>
      )}

      {/* Sections du formulaire */}
      <div className={`${layoutClass} ${columnsClass}`}>
        {config.sections
          .sort((a, b) => (a.order || 0) - (b.order || 0))
          .map((section) => renderSection(section))}
      </div>

      {/* Message de succès global */}
      {state.isValid && !state.isDirty && config.messages?.success && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-green-800">{config.messages.success}</p>
        </div>
      )}

      {/* Message d'erreur global */}
      {Object.keys(state.errors).length > 0 && config.messages?.error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">{config.messages.error}</p>
        </div>
      )}

      {/* Boutons d'action */}
      {(showSubmitButton || showCancel) && (
        <div className={`mt-8 flex gap-4 ${buttonPositionClass}`}>
          {showCancel && (
            <Button
              type="button"
              onClick={handleCancel}
              variant="secondary"
              disabled={state.isSubmitting}
            >
              {finalCancelLabel}
            </Button>
          )}

          {showSubmitButton && (
            <Button
              type="submit"
              disabled={state.isSubmitting || config.submitButton?.disabled}
              variant="primary"
            >
              {state.isSubmitting ? 'Envoi en cours...' : finalSubmitLabel}
            </Button>
          )}
        </div>
      )}

      {/* Indicateur de sauvegarde automatique */}
      {config.autosave?.enabled && state.isDirty && (
        <div className="mt-4 text-sm text-gray-500 text-center">
          💾 Sauvegarde automatique activée
        </div>
      )}
    </form>
  );
};

export default DynamicForm;
