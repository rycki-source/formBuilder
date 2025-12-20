/**
 * Utilitaire pour rendre les champs dynamiquement
 * Mappe les types de champs vers les composants appropriés
 */

/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';
import type { FieldConfig, FieldOption } from '../types/referentiel.types';
import { Input } from '../../../components/Input';

export interface FieldRendererProps {
  field: FieldConfig;
  value: any;
  onChange: (value: any) => void;
  onBlur?: () => void;
  error?: string;
  disabled?: boolean;
}

/**
 * Composants de champs personnalisés
 */
const FieldComponents = {
  // Champs texte
  text: (props: FieldRendererProps) => (
    <Input
      type="text"
      id={props.field.id}
      name={props.field.name}
      placeholder={props.field.placeholder}
      value={props.value || ''}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      readOnly={props.field.readonly}
      minLength={props.field.minLength}
      maxLength={props.field.maxLength}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  email: (props: FieldRendererProps) => (
    <Input
      type="email"
      id={props.field.id}
      name={props.field.name}
      placeholder={props.field.placeholder}
      value={props.value || ''}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      readOnly={props.field.readonly}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  password: (props: FieldRendererProps) => (
    <Input
      type="password"
      id={props.field.id}
      name={props.field.name}
      placeholder={props.field.placeholder}
      value={props.value || ''}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      readOnly={props.field.readonly}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  tel: (props: FieldRendererProps) => (
    <Input
      type="tel"
      id={props.field.id}
      name={props.field.name}
      placeholder={props.field.placeholder}
      value={props.value || ''}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      readOnly={props.field.readonly}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  url: (props: FieldRendererProps) => (
    <Input
      type="url"
      id={props.field.id}
      name={props.field.name}
      placeholder={props.field.placeholder}
      value={props.value || ''}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      readOnly={props.field.readonly}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  // Zone de texte
  textarea: (props: FieldRendererProps) => (
    <textarea
      id={props.field.id}
      name={props.field.name}
      placeholder={props.field.placeholder}
      value={props.value || ''}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      readOnly={props.field.readonly}
      rows={props.field.rows || 4}
      minLength={props.field.minLength}
      maxLength={props.field.maxLength}
      className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${props.field.className || ''}`}
      style={props.field.style}
    />
  ),

  // Champs numériques
  number: (props: FieldRendererProps) => (
    <Input
      type="number"
      id={props.field.id}
      name={props.field.name}
      placeholder={props.field.placeholder}
      value={props.value ?? ''}
      onChange={(e) => props.onChange(e.target.value ? Number(e.target.value) : null)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      readOnly={props.field.readonly}
      min={props.field.min}
      max={props.field.max}
      step={props.field.step}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  range: (props: FieldRendererProps) => (
    <div className="space-y-2">
      <input
        type="range"
        id={props.field.id}
        name={props.field.name}
        value={props.value ?? props.field.min ?? 0}
        onChange={(e) => props.onChange(Number(e.target.value))}
        onBlur={props.onBlur}
        disabled={props.disabled || props.field.disabled}
        min={props.field.min}
        max={props.field.max}
        step={props.field.step}
        className={`w-full ${props.field.className || ''}`}
        aria-label={props.field.label || props.field.name}
        title={props.field.label || props.field.name}
      />
      <div className="text-sm text-gray-600 text-center">
        {props.value ?? props.field.min ?? 0}
      </div>
    </div>
  ),

  // Champs de date/heure
  date: (props: FieldRendererProps) => (
    <Input
      type="date"
      id={props.field.id}
      name={props.field.name}
      value={props.value || ''}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      readOnly={props.field.readonly}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  'datetime-local': (props: FieldRendererProps) => (
    <Input
      type="datetime-local"
      id={props.field.id}
      name={props.field.name}
      value={props.value || ''}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      readOnly={props.field.readonly}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  time: (props: FieldRendererProps) => (
    <Input
      type="time"
      id={props.field.id}
      name={props.field.name}
      value={props.value || ''}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      readOnly={props.field.readonly}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  month: (props: FieldRendererProps) => (
    <Input
      type="month"
      id={props.field.id}
      name={props.field.name}
      value={props.value || ''}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      readOnly={props.field.readonly}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  week: (props: FieldRendererProps) => (
    <Input
      type="week"
      id={props.field.id}
      name={props.field.name}
      value={props.value || ''}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      readOnly={props.field.readonly}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  // Select
  select: (props: FieldRendererProps) => (
    <select
      id={props.field.id}
      name={props.field.name}
      value={props.value || ''}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${props.field.className || ''}`}
      style={props.field.style}
      aria-label={props.field.label || props.field.name}
    >
      {props.field.placeholder && (
        <option value="">{props.field.placeholder}</option>
      )}
      {props.field.options?.map((option: FieldOption) => (
        <option
          key={option.value}
          value={option.value}
          disabled={option.disabled}
        >
          {option.label}
        </option>
      ))}
    </select>
  ),

  multiselect: (props: FieldRendererProps) => (
    <select
      id={props.field.id}
      name={props.field.name}
      value={props.value || []}
      onChange={(e) => {
        const selected = Array.from(e.target.selectedOptions).map(o => o.value);
        props.onChange(selected);
      }}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      multiple
      className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${props.field.className || ''}`}
      style={props.field.style}
      aria-label={props.field.label || props.field.name}
    >
      {props.field.options?.map((option: FieldOption) => (
        <option
          key={option.value}
          value={option.value}
          disabled={option.disabled}
        >
          {option.label}
        </option>
      ))}
    </select>
  ),

  // Radio buttons
  radio: (props: FieldRendererProps) => (
    <div className={`space-y-2 ${props.field.className || ''}`}>
      {props.field.options?.map((option: FieldOption) => (
        <label key={option.value} className="flex items-center space-x-2">
          <input
            type="radio"
            name={props.field.name}
            value={option.value}
            checked={props.value === option.value}
            onChange={() => props.onChange(option.value)}
            onBlur={props.onBlur}
            disabled={props.disabled || props.field.disabled || option.disabled}
            className="text-blue-500 focus:ring-blue-500"
          />
          <span>{option.label}</span>
          {option.description && (
            <span className="text-sm text-gray-500">({option.description})</span>
          )}
        </label>
      ))}
    </div>
  ),

  // Checkbox unique
  checkbox: (props: FieldRendererProps) => (
    <label className={`flex items-center space-x-2 ${props.field.className || ''}`}>
      <input
        type="checkbox"
        id={props.field.id}
        name={props.field.name}
        checked={props.value || false}
        onChange={(e) => props.onChange(e.target.checked)}
        onBlur={props.onBlur}
        disabled={props.disabled || props.field.disabled}
        className="text-blue-500 focus:ring-blue-500"
      />
      <span>{props.field.label}</span>
    </label>
  ),

  // Switch (toggle)
  switch: (props: FieldRendererProps) => (
    <label className={`inline-flex items-center cursor-pointer ${props.field.className || ''}`}>
      <input
        type="checkbox"
        id={props.field.id}
        name={props.field.name}
        checked={props.value || false}
        onChange={(e) => props.onChange(e.target.checked)}
        onBlur={props.onBlur}
        disabled={props.disabled || props.field.disabled}
        className="sr-only peer"
        aria-label={props.field.label || props.field.name}
      />
      <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:start-0.5 after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
    </label>
  ),

  // Fichier
  file: (props: FieldRendererProps) => (
    <Input
      type="file"
      id={props.field.id}
      name={props.field.name}
      onChange={(e) => {
        const files = e.target.files;
        props.onChange(props.field.multiple ? Array.from(files || []) : files?.[0]);
      }}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      accept={props.field.accept}
      multiple={props.field.multiple}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  // Couleur
  color: (props: FieldRendererProps) => (
    <Input
      type="color"
      id={props.field.id}
      name={props.field.name}
      value={props.value || '#000000'}
      onChange={(e) => props.onChange(e.target.value)}
      onBlur={props.onBlur}
      disabled={props.disabled || props.field.disabled}
      className={props.field.className}
      style={props.field.style}
    />
  ),

  // Champ caché
  hidden: (props: FieldRendererProps) => (
    <input
      type="hidden"
      id={props.field.id}
      name={props.field.name}
      value={props.value || ''}
    />
  ),

  // Géolocalisation
  geolocation: (props: FieldRendererProps) => {
    const GeolocationField = React.lazy(() => import('../../../components/GeolocationField'));
    return (
      <React.Suspense fallback={<div>Chargement...</div>}>
        <GeolocationField
          value={props.value}
          onChange={props.onChange}
          label={props.field.label || props.field.name}
          required={props.field.required}
          disabled={props.disabled || props.field.disabled}
          error={props.error}
        />
      </React.Suspense>
    );
  },

  // Signature
  signature: (props: FieldRendererProps) => {
    const SignatureField = React.lazy(() => import('../../../components/SignatureField'));
    return (
      <React.Suspense fallback={<div>Chargement...</div>}>
        <SignatureField
          value={props.value}
          onChange={props.onChange}
          label={props.field.label || props.field.name}
          required={props.field.required}
          disabled={props.disabled || props.field.disabled}
          error={props.error}
        />
      </React.Suspense>
    );
  },
};

/**
 * Rend un champ selon son type
 */
export function renderField(props: FieldRendererProps): React.ReactNode {
  const Component = FieldComponents[props.field.type as keyof typeof FieldComponents];

  if (!Component) {
    console.warn(`Type de champ non supporté: ${props.field.type}`);
    return null;
  }

  return Component(props);
}

/**
 * Obtient la valeur par défaut d'un champ
 */
export function getDefaultValue(field: FieldConfig): any {
  if (field.defaultValue !== undefined) {
    return field.defaultValue;
  }

  switch (field.type) {
    case 'checkbox':
    case 'switch':
      return false;
    case 'multiselect':
      return [];
    case 'number':
    case 'range':
      return field.min ?? 0;
    default:
      return '';
  }
}

/**
 * Formatte la valeur d'un champ pour l'affichage
 */
export function formatFieldValue(field: FieldConfig, value: any): string {
  if (value === null || value === undefined) {
    return '';
  }

  switch (field.type) {
    case 'checkbox':
    case 'switch':
      return value ? 'Oui' : 'Non';

    case 'select':
    case 'radio': {
      const option = field.options?.find(o => o.value === value);
      return option?.label || String(value);
    }

    case 'multiselect':
      if (Array.isArray(value)) {
        return value
          .map(v => field.options?.find(o => o.value === v)?.label || v)
          .join(', ');
      }
      return '';

    case 'file':
      if (value instanceof File) {
        return value.name;
      }
      if (Array.isArray(value)) {
        return value.map(f => f.name).join(', ');
      }
      return '';

    case 'date':
      return new Date(value).toLocaleDateString('fr-FR');

    case 'datetime-local':
      return new Date(value).toLocaleString('fr-FR');

    default:
      return String(value);
  }
}
