import { useState } from 'react';
import { Plus, Trash2, ChevronUp, ChevronDown } from 'lucide-react';
import { Card } from '../../components/Card';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import type { EtapeFormulaire, ChampFormulaire } from '../../types';

interface StepManagerProps {
  etapes: EtapeFormulaire[];
  champs: ChampFormulaire[];
  onUpdateEtapes: (etapes: EtapeFormulaire[]) => void;
}

export const StepManager = ({ etapes, champs, onUpdateEtapes }: StepManagerProps) => {
  const [selectedStep, setSelectedStep] = useState<number>(0);

  const handleAddStep = () => {
    const newStep: EtapeFormulaire = {
      id: `step-${Date.now()}`,
      titre: `Étape ${etapes.length + 1}`,
      description: '',
      champs: []
    };
    onUpdateEtapes([...etapes, newStep]);
    setSelectedStep(etapes.length);
  };

  const handleDeleteStep = (stepId: string) => {
    if (etapes.length <= 1) {
      alert('Vous devez avoir au moins une étape');
      return;
    }
    const newEtapes = etapes.filter((etape) => etape.id !== stepId);
    onUpdateEtapes(newEtapes);
    if (selectedStep >= newEtapes.length) {
      setSelectedStep(newEtapes.length - 1);
    }
  };

  const handleMoveStep = (index: number, direction: 'up' | 'down') => {
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= etapes.length) return;

    const newEtapes = [...etapes];
    [newEtapes[index], newEtapes[newIndex]] = [newEtapes[newIndex], newEtapes[index]];
    onUpdateEtapes(newEtapes);
    setSelectedStep(newIndex);
  };

  const handleUpdateStep = (index: number, updates: Partial<EtapeFormulaire>) => {
    const newEtapes = [...etapes];
    newEtapes[index] = { ...newEtapes[index], ...updates };
    onUpdateEtapes(newEtapes);
  };

  const handleAssignFieldToStep = (fieldIndex: number, stepIndex: number) => {
    const field = champs[fieldIndex];
    const newEtapes = [...etapes];
    
    // Retirer le champ de toutes les étapes
    newEtapes.forEach(etape => {
      etape.champs = etape.champs.filter(c => c.id !== field.id);
    });

    // Ajouter le champ à l'étape sélectionnée
    if (!newEtapes[stepIndex].champs) {
      newEtapes[stepIndex].champs = [];
    }
    newEtapes[stepIndex].champs.push(field);
    
    onUpdateEtapes(newEtapes);
  };

  const getUnassignedFields = () => {
    const assignedFieldIds = new Set(
      etapes.flatMap(etape => etape.champs?.map(c => c.id) || [])
    );
    return champs.filter(field => !assignedFieldIds.has(field.id));
  };

  return (
    <div className="space-y-4">
      <Card title="Gestion des étapes">
        {/* Liste des étapes */}
        <div className="space-y-2 mb-4">
          {etapes.map((etape, index) => (
            <div
              key={etape.id}
              className={`p-3 border-2 rounded-lg cursor-pointer transition-colors ${
                selectedStep === index
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-300 bg-white hover:border-blue-400'
              }`}
              onClick={() => setSelectedStep(index)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{etape.titre}</h4>
                  <p className="text-xs text-gray-600">
                    {etape.champs?.length || 0} champ(s)
                  </p>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleMoveStep(index, 'up');
                    }}
                    disabled={index === 0}
                    aria-label="Monter l'étape"
                    className="p-1 text-gray-400 hover:text-blue-600 disabled:opacity-30"
                  >
                    <ChevronUp className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleMoveStep(index, 'down');
                    }}
                    disabled={index === etapes.length - 1}
                    aria-label="Descendre l'étape"
                    className="p-1 text-gray-400 hover:text-blue-600 disabled:opacity-30"
                  >
                    <ChevronDown className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteStep(etape.id);
                    }}
                    aria-label="Supprimer l'étape"
                    className="p-1 text-gray-400 hover:text-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <Button onClick={handleAddStep} variant="secondary" size="sm">
          <Plus className="w-4 h-4 mr-2" />
          Ajouter une étape
        </Button>
      </Card>

      {/* Configuration de l'étape sélectionnée */}
      {etapes[selectedStep] && (
        <Card title={`Configuration: ${etapes[selectedStep].titre}`}>
          <div className="space-y-4">
            <Input
              label="Titre de l'étape"
              value={etapes[selectedStep].titre}
              onChange={(e) => handleUpdateStep(selectedStep, { titre: e.target.value })}
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description (optionnelle)
              </label>
              <textarea
                value={etapes[selectedStep].description || ''}
                onChange={(e) => handleUpdateStep(selectedStep, { description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={2}
                placeholder="Description de cette étape..."
              />
            </div>

            {/* Champs de cette étape */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Champs dans cette étape ({etapes[selectedStep].champs?.length || 0})
              </h4>
              <div className="space-y-1 mb-3">
                {etapes[selectedStep].champs?.map((field) => (
                  <div
                    key={field.id}
                    className="px-3 py-2 bg-blue-100 text-blue-800 rounded text-sm"
                  >
                    {field.label} ({field.type_champ})
                  </div>
                ))}
              </div>
            </div>

            {/* Champs non assignés */}
            {getUnassignedFields().length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  Champs non assignés ({getUnassignedFields().length})
                </h4>
                <div className="space-y-1">
                  {getUnassignedFields().map((field) => (
                    <button
                      key={field.id}
                      onClick={() => {
                        const fieldIndex = champs.findIndex(f => f.id === field.id);
                        handleAssignFieldToStep(fieldIndex, selectedStep);
                      }}
                      className="w-full px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded text-sm text-left transition-colors"
                    >
                      + {field.label} ({field.type_champ})
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};
