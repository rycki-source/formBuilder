import { useState } from 'react';
import { ChevronLeft, ChevronRight, Check } from 'lucide-react';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { Input } from '../components/Input';
import type { ChampFormulaire, EtapeFormulaire } from '../types';

interface MultiStepFormPreviewProps {
  etapes: EtapeFormulaire[];
  onSubmit: (data: Record<string, unknown>) => void;
  isModal?: boolean;
}

export const MultiStepFormPreview = ({ etapes, onSubmit, isModal = false }: MultiStepFormPreviewProps) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<Record<string, unknown>>({});

  const handleInputChange = (fieldLabel: string, value: unknown) => {
    setFormData(prev => ({ ...prev, [fieldLabel]: value }));
  };

  const validateCurrentStep = () => {
    const currentFields = etapes[currentStep]?.champs || [];
    const requiredFields = currentFields.filter(f => f.obligatoire);
    const missingFields = requiredFields.filter(f => !formData[f.label]);
    
    if (missingFields.length > 0) {
      alert(`Veuillez remplir les champs obligatoires : ${missingFields.map(f => f.label).join(', ')}`);
      return false;
    }
    return true;
  };

  const handleNext = () => {
    if (validateCurrentStep()) {
      if (currentStep < etapes.length - 1) {
        setCurrentStep(currentStep + 1);
      }
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateCurrentStep()) {
      onSubmit(formData);
    }
  };

  const renderField = (field: ChampFormulaire) => {
    switch (field.type_champ) {
      case 'text':
      case 'email':
        return (
          <Input
            key={field.label}
            label={field.label}
            type={field.type_champ}
            placeholder={field.placeholder}
            required={field.obligatoire}
            value={formData[field.label] as string || ''}
            onChange={(e) => handleInputChange(field.label, e.target.value)}
          />
        );

      case 'number':
        return (
          <Input
            key={field.label}
            label={field.label}
            type="number"
            placeholder={field.placeholder}
            required={field.obligatoire}
            value={formData[field.label] as string || ''}
            onChange={(e) => handleInputChange(field.label, e.target.value)}
          />
        );

      case 'date':
        return (
          <Input
            key={field.label}
            label={field.label}
            type="date"
            required={field.obligatoire}
            value={formData[field.label] as string || ''}
            onChange={(e) => handleInputChange(field.label, e.target.value)}
          />
        );

      case 'textarea':
        return (
          <div key={field.label}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label} {field.obligatoire && <span className="text-red-500">*</span>}
            </label>
            <textarea
              value={formData[field.label] as string || ''}
              onChange={(e) => handleInputChange(field.label, e.target.value)}
              placeholder={field.placeholder}
              required={field.obligatoire}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={4}
            />
          </div>
        );

      case 'select':
        return (
          <div key={field.label}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label} {field.obligatoire && <span className="text-red-500">*</span>}
            </label>
            <select
              value={formData[field.label] as string || ''}
              onChange={(e) => handleInputChange(field.label, e.target.value)}
              required={field.obligatoire}
              aria-label={field.label}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Sélectionnez une option</option>
              {field.options?.map((option, idx) => (
                <option key={idx} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        );

      case 'checkbox':
        return (
          <div key={field.label} className="flex items-center">
            <input
              type="checkbox"
              checked={formData[field.label] as boolean || false}
              onChange={(e) => handleInputChange(field.label, e.target.checked)}
              required={field.obligatoire}
              aria-label={field.label}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label className="ml-2 text-sm text-gray-700">
              {field.label} {field.obligatoire && <span className="text-red-500">*</span>}
            </label>
          </div>
        );

      case 'radio':
        return (
          <div key={field.label}>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {field.label} {field.obligatoire && <span className="text-red-500">*</span>}
            </label>
            <div className="space-y-2">
              {field.options?.map((option, idx) => (
                <div key={idx} className="flex items-center">
                  <input
                    type="radio"
                    name={field.label}
                    value={option}
                    checked={formData[field.label] === option}
                    onChange={(e) => handleInputChange(field.label, e.target.value)}
                    required={field.obligatoire}
                    aria-label={`${field.label} - ${option}`}
                    className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <label className="ml-2 text-sm text-gray-700">{option}</label>
                </div>
              ))}
            </div>
          </div>
        );

      case 'file':
        return (
          <div key={field.label}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label} {field.obligatoire && <span className="text-red-500">*</span>}
            </label>
            <input
              type="file"
              onChange={(e) => handleInputChange(field.label, e.target.files?.[0])}
              required={field.obligatoire}
              aria-label={field.label}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        );

      case 'button':
        return null; // Les boutons sont gérés séparément

      default:
        return null;
    }
  };

  const containerClass = isModal 
    ? "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    : "";

  const content = (
    <Card title={etapes[currentStep]?.titre || `Étape ${currentStep + 1}`}>
      {/* Barre de progression */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          {etapes.map((etape, index) => (
            <div key={etape.id} className="flex items-center flex-1">
              <div
                className={`flex items-center justify-center w-8 h-8 rounded-full font-semibold ${
                  index < currentStep
                    ? 'bg-green-500 text-white'
                    : index === currentStep
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}
              >
                {index < currentStep ? <Check className="w-5 h-5" /> : index + 1}
              </div>
              {index < etapes.length - 1 && (
                <div
                  className={`flex-1 h-1 mx-2 ${
                    index < currentStep ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
        <p className="text-sm text-gray-600 text-center">
          Étape {currentStep + 1} sur {etapes.length}
        </p>
      </div>

      {/* Description de l'étape */}
      {etapes[currentStep]?.description && (
        <p className="text-gray-600 mb-6">{etapes[currentStep].description}</p>
      )}

      {/* Formulaire de l'étape courante */}
      <form onSubmit={handleSubmit}>
        <div className="space-y-4 mb-6">
          {etapes[currentStep]?.champs?.map((field) => renderField(field))}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center pt-4 border-t border-gray-200">
          <Button
            type="button"
            variant="secondary"
            onClick={handlePrevious}
            disabled={currentStep === 0}
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Précédent
          </Button>

          {currentStep < etapes.length - 1 ? (
            <Button type="button" variant="primary" onClick={handleNext}>
              Suivant
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button type="submit" variant="primary">
              <Check className="w-4 h-4 mr-2" />
              Soumettre
            </Button>
          )}
        </div>
      </form>
    </Card>
  );

  return isModal ? (
    <div className={containerClass}>
      <div className="max-w-2xl w-full">{content}</div>
    </div>
  ) : (
    content
  );
};
