import { useState } from 'react';
import { X, Plus, Trash2, Shield } from 'lucide-react';
import { Card } from '../../components/Card';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';
import type { ChampFormulaire } from '../../types';

interface ValidationRule {
  type: 'required' | 'email' | 'pattern' | 'minLength' | 'maxLength' | 'min' | 'max';
  message: string;
  value?: string | number;
  pattern?: string;
}

interface FieldEditorProps {
  field: ChampFormulaire;
  onUpdateField: (updates: Partial<ChampFormulaire>) => void;
  onClose: () => void;
}

export const FieldEditor = ({ field, onUpdateField, onClose }: FieldEditorProps) => {
  const [newOption, setNewOption] = useState('');
  const [showValidationRules, setShowValidationRules] = useState(false);

  const handleAddOption = () => {
    if (newOption.trim()) {
      const updatedOptions = [...(field.options || []), newOption.trim()];
      onUpdateField({ options: updatedOptions });
      setNewOption('');
    }
  };

  const handleDeleteOption = (index: number) => {
    const updatedOptions = (field.options || []).filter((_, i) => i !== index);
    onUpdateField({ options: updatedOptions });
  };

  const handleAddValidationRule = (ruleType: ValidationRule['type']) => {
    const validationRules = (field.validation_rules as ValidationRule[]) || [];
    
    const defaultMessages: Record<string, string> = {
      required: 'Ce champ est obligatoire',
      email: 'Format email invalide',
      pattern: 'Format invalide',
      minLength: 'Minimum {value} caractères',
      maxLength: 'Maximum {value} caractères',
      min: 'Valeur minimum: {value}',
      max: 'Valeur maximum: {value}',
    };

    const newRule: ValidationRule = {
      type: ruleType,
      message: defaultMessages[ruleType] || 'Validation échouée',
      ...(ruleType === 'minLength' || ruleType === 'maxLength' ? { value: 1 } : {}),
      ...(ruleType === 'min' || ruleType === 'max' ? { value: 0 } : {}),
      ...(ruleType === 'pattern' ? { pattern: '' } : {}),
    };

    onUpdateField({ validation_rules: [...validationRules, newRule] });
  };

  const handleUpdateValidationRule = (index: number, updates: Partial<ValidationRule>) => {
    const validationRules = [...((field.validation_rules as ValidationRule[]) || [])];
    validationRules[index] = { ...validationRules[index], ...updates };
    onUpdateField({ validation_rules: validationRules });
  };

  const handleDeleteValidationRule = (index: number) => {
    const validationRules = ((field.validation_rules as ValidationRule[]) || []).filter((_: ValidationRule, i: number) => i !== index);
    onUpdateField({ validation_rules: validationRules });
  };

  const showOptions = field.type_champ === 'select' || field.type_champ === 'radio';
  const canHaveValidation = field.type_champ !== 'button';
  const validationRules = (field.validation_rules as ValidationRule[]) || [];

  return (
    <Card
      title="Propriétés du champ"
      className="sticky top-24"
      headerAction={
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600" title="Fermer">
          <X className="w-5 h-5" />
        </button>
      }
    >
      <div className="space-y-4">
        <Input
          label="Label"
          value={field.label}
          onChange={(e) => onUpdateField({ label: e.target.value })}
          placeholder="Nom du champ"
        />

        <Input
          label="Placeholder"
          value={field.placeholder || ''}
          onChange={(e) => onUpdateField({ placeholder: e.target.value })}
          placeholder="Texte d'aide"
        />

        {field.type_champ !== 'button' && (
          <div className="flex items-center">
            <input
              type="checkbox"
              id="obligatoire"
              checked={field.obligatoire}
              onChange={(e) => onUpdateField({ obligatoire: e.target.checked })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="obligatoire" className="ml-2 text-sm font-medium text-gray-700">
              Champ obligatoire
            </label>
          </div>
        )}

        {field.type_champ === 'button' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type de bouton
              </label>
              <select
                value={field.buttonType || 'button'}
                onChange={(e) => onUpdateField({ buttonType: e.target.value as 'submit' | 'reset' | 'button' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                title="Type de bouton"
              >
                <option value="submit">Submit (Envoyer)</option>
                <option value="button">Button (Action)</option>
                <option value="reset">Reset (Réinitialiser)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Style
              </label>
              <select
                value={field.buttonStyle || 'primary'}
                onChange={(e) => onUpdateField({ buttonStyle: e.target.value as 'primary' | 'secondary' | 'danger' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                title="Style"
              >
                <option value="primary">Primaire (Bleu)</option>
                <option value="secondary">Secondaire (Gris)</option>
                <option value="danger">Danger (Rouge)</option>
              </select>
            </div>
          </>
        )}

        {showOptions && (
          <div className="border-t border-gray-200 pt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Options
            </label>
            <div className="space-y-2 mb-3">
              {(field.options || []).map((option, index) => (
                <div key={index} className="flex items-center gap-2">
                  <input
                    type="text"
                    value={option}
                    onChange={(e) => {
                      const updatedOptions = [...(field.options || [])];
                      updatedOptions[index] = e.target.value;
                      onUpdateField({ options: updatedOptions });
                    }}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    placeholder={`Option ${index + 1}`}
                  />
                  <button
                    onClick={() => handleDeleteOption(index)}
                    className="text-gray-400 hover:text-red-500"
                    title="Supprimer l'option"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={newOption}
                onChange={(e) => setNewOption(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddOption()}
                placeholder="Nouvelle option"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
              <Button size="sm" onClick={handleAddOption}>
                <Plus className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}

        {canHaveValidation && (
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between mb-3">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Shield className="w-4 h-4" />
                Règles de validation
              </label>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowValidationRules(!showValidationRules)}
              >
                {showValidationRules ? 'Masquer' : 'Afficher'}
              </Button>
            </div>

            {showValidationRules && (
              <div className="space-y-3">
                {validationRules.length === 0 && (
                  <p className="text-xs text-gray-500 italic">
                    Aucune règle de validation. Ajoutez-en pour sécuriser vos données.
                  </p>
                )}

                {validationRules.map((rule, index) => (
                  <div key={index} className="bg-gray-50 p-3 rounded-lg space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-gray-700 uppercase">
                        {rule.type}
                      </span>
                      <button
                        onClick={() => handleDeleteValidationRule(index)}
                        className="text-gray-400 hover:text-red-500"
                        title="Supprimer la règle"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>

                    <Input
                      label="Message d'erreur"
                      value={rule.message}
                      onChange={(e) => handleUpdateValidationRule(index, { message: e.target.value })}
                      placeholder="Message affiché si la validation échoue"
                    />

                    {(rule.type === 'minLength' || rule.type === 'maxLength' || rule.type === 'min' || rule.type === 'max') && (
                      <Input
                        label="Valeur"
                        type="number"
                        value={rule.value || 0}
                        onChange={(e) => handleUpdateValidationRule(index, { value: parseInt(e.target.value) })}
                        placeholder="Valeur de validation"
                      />
                    )}

                    {rule.type === 'pattern' && (
                      <Input
                        label="Pattern (Regex)"
                        value={rule.pattern || ''}
                        onChange={(e) => handleUpdateValidationRule(index, { pattern: e.target.value })}
                        placeholder="^[A-Za-z]+$"
                      />
                    )}
                  </div>
                ))}

                <div className="border-t border-gray-200 pt-3">
                  <label className="block text-xs font-medium text-gray-600 mb-2">
                    Ajouter une règle :
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {field.type_champ !== 'checkbox' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAddValidationRule('required')}
                        className="text-xs"
                      >
                        Obligatoire
                      </Button>
                    )}
                    {(field.type_champ === 'text' || field.type_champ === 'email') && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAddValidationRule('email')}
                          className="text-xs"
                        >
                          Email
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAddValidationRule('minLength')}
                          className="text-xs"
                        >
                          Long. min
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAddValidationRule('maxLength')}
                          className="text-xs"
                        >
                          Long. max
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAddValidationRule('pattern')}
                          className="text-xs"
                        >
                          Pattern
                        </Button>
                      </>
                    )}
                    {field.type_champ === 'number' && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAddValidationRule('min')}
                          className="text-xs"
                        >
                          Min
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAddValidationRule('max')}
                          className="text-xs"
                        >
                          Max
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="border-t border-gray-200 pt-4">
          <p className="text-xs text-gray-500">
            Type de champ: <span className="font-medium">{field.type_champ}</span>
          </p>
        </div>
      </div>
    </Card>
  );
};
