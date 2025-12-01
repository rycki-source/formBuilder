import { useState } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { Card } from '../../components/Card';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';
import type { ChampFormulaire } from '../../types';

interface FieldEditorProps {
  field: ChampFormulaire;
  onUpdateField: (updates: Partial<ChampFormulaire>) => void;
  onClose: () => void;
}

export const FieldEditor = ({ field, onUpdateField, onClose }: FieldEditorProps) => {
  const [newOption, setNewOption] = useState('');

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

  const showOptions = field.type_champ === 'select' || field.type_champ === 'radio';

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

        <div className="border-t border-gray-200 pt-4">
          <p className="text-xs text-gray-500">
            Type de champ: <span className="font-medium">{field.type_champ}</span>
          </p>
        </div>
      </div>
    </Card>
  );
};
