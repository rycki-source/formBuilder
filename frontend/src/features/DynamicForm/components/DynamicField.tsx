/**
 * Composant pour rendre un champ dynamique individuel
 */

/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';
import type { FieldConfig } from '../types/referentiel.types';
import { renderField } from '../utils/fieldRenderer';

export interface DynamicFieldProps {
  field: FieldConfig;
  value: any;
  error?: string;
  touched?: boolean;
  disabled?: boolean;
  onChange: (value: any) => void;
  onBlur?: () => void;
}

const DynamicField: React.FC<DynamicFieldProps> = ({
  field,
  value,
  error,
  touched,
  disabled,
  onChange,
  onBlur
}) => {
  // Ne pas afficher les champs cachés dans le layout normal
  if (field.type === 'hidden') {
    return renderField({ field, value, onChange, onBlur, error, disabled }) as React.ReactElement;
  }

  // Calculer les classes de largeur pour le grid
  const widthClass = field.width
    ? typeof field.width === 'string'
      ? field.width
      : `w-[${field.width}px]`
    : 'w-full';

  const spanClass = field.span ? `col-span-${field.span}` : '';

  return (
    <div className={`${widthClass} ${spanClass} ${field.className || ''}`}>
      {/* Label */}
      {field.label && field.type !== 'checkbox' && field.type !== 'switch' && (
        <label
          htmlFor={field.id}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {field.label}
          {field.required && <span className="text-red-500 ml-1">*</span>}
          {field.tooltip && (
            <span
              className="ml-2 text-gray-400 cursor-help"
              title={field.tooltip}
            >
              ℹ️
            </span>
          )}
        </label>
      )}

      {/* Champ */}
      <div className="relative">
        {renderField({
          field,
          value,
          onChange,
          onBlur,
          error,
          disabled
        })}
      </div>

      {/* Description */}
      {field.description && (
        <p className="mt-1 text-sm text-gray-500">{field.description}</p>
      )}

      {/* Erreur */}
      {touched && error && (
        <p className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      {/* Indicateur de champ calculé */}
      {field.computed && field.readonly && (
        <p className="mt-1 text-xs text-blue-600 italic">
          Calculé automatiquement
        </p>
      )}
    </div>
  );
};

export default DynamicField;
