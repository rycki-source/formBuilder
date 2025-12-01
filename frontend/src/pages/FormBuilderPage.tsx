import { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { DndContext, closestCenter } from '@dnd-kit/core';
import type { DragEndEvent } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { Save, Eye, ArrowLeft } from 'lucide-react';
import { useFormBuilderStore } from '../store/formBuilderStore';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card } from '../components/Card';
import { FieldList, FieldEditor, FieldPalette, StepManager } from '../features/FormBuilder';
import type { ChampFormulaire, FormulaireCreate } from '../types';

export const FormBuilderPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const {
    currentFormulaire,
    fetchFormulaireById,
    createFormulaire,
    updateFormulaire,
    setCurrentFormulaire,
    updateCurrentFormulaire,
    initializeFromTemplate,
    addChamp,
    updateChamp,
    removeChamp,
    reorderChamps,
  } = useFormBuilderStore();

  const [selectedFieldIndex, setSelectedFieldIndex] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<'fields' | 'steps'>('fields');

  const isMultiStep = currentFormulaire?.type_structurel === 'multi-etapes' || currentFormulaire?.type_structurel === 'wizard';

  useEffect(() => {
    if (id && id !== 'nouveau') {
      fetchFormulaireById(id);
    } else {
      // Nouveau formulaire - vérifier s'il y a un template
      const state = location.state as { 
        typeStructurel?: string; 
        typeFonctionnel?: string; 
        template?: { champs: ChampFormulaire[] } 
      } | null;
      
      if (state?.typeStructurel && state?.typeFonctionnel) {
        initializeFromTemplate(
          state.typeStructurel,
          state.typeFonctionnel,
          state.template?.champs || []
        );
      } else {
        // Formulaire vierge par défaut
        setCurrentFormulaire({
          nom: '',
          description: '',
          type_structurel: 'simple',
          type_fonctionnel: 'personnalise',
          structure_json: { champs: [] },
          publie: false,
        });
      }
    }
  }, [id, fetchFormulaireById, setCurrentFormulaire, initializeFromTemplate, location.state]);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = currentFormulaire?.structure_json.champs.findIndex((_, i) => i === Number(active.id));
      const newIndex = currentFormulaire?.structure_json.champs.findIndex((_, i) => i === Number(over.id));
      if (oldIndex !== undefined && newIndex !== undefined && oldIndex !== -1 && newIndex !== -1) {
        reorderChamps(oldIndex, newIndex);
      }
    }
  };

  const handleAddField = (type: ChampFormulaire['type_champ']) => {
    const newField: ChampFormulaire = {
      label: `Nouveau champ ${type}`,
      type_champ: type,
      obligatoire: false,
      ordre: currentFormulaire?.structure_json.champs.length || 0,
      placeholder: '',
      options: type === 'select' || type === 'radio' ? ['Option 1', 'Option 2'] : undefined,
    };
    addChamp(newField);
    setSelectedFieldIndex((currentFormulaire?.structure_json.champs.length || 0));
  };

  const handleSave = async () => {
    if (!currentFormulaire?.nom?.trim()) {
      alert('Veuillez saisir un nom pour le formulaire');
      return;
    }

    if (!currentFormulaire?.structure_json?.champs || currentFormulaire.structure_json.champs.length === 0) {
      alert('Veuillez ajouter au moins un champ au formulaire');
      return;
    }

    const formData: FormulaireCreate = {
      nom: currentFormulaire.nom,
      description: currentFormulaire.description,
      type_structurel: currentFormulaire.type_structurel || 'simple',
      type_fonctionnel: currentFormulaire.type_fonctionnel || 'personnalise',
      structure_json: currentFormulaire.structure_json,
    };

    try {
      if (id && id !== 'nouveau') {
        await updateFormulaire(id, formData);
        alert('Formulaire mis à jour avec succès');
      } else {
        const newForm = await createFormulaire(formData);
        alert('Formulaire créé avec succès');
        navigate(`/formulaires/${newForm.id}`);
      }
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
      alert('Erreur lors de la sauvegarde du formulaire');
    }
  };

  const handlePreview = () => {
    if (id && id !== 'nouveau') {
      navigate(`/formulaires/${id}/preview`);
    } else {
      alert('Veuillez d\'abord enregistrer le formulaire');
    }
  };

  if (!currentFormulaire) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="outline" size="sm" onClick={() => navigate('/formulaires')}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Retour
              </Button>
              <h1 className="text-2xl font-bold text-gray-900">
                {id && id !== 'nouveau' ? 'Éditer le formulaire' : 'Nouveau formulaire'}
              </h1>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={handlePreview}>
                <Eye className="w-4 h-4 mr-2" />
                Aperçu
              </Button>
              <Button variant="primary" onClick={handleSave}>
                <Save className="w-4 h-4 mr-2" />
                Enregistrer
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Palette de champs */}
          <div className="col-span-12 lg:col-span-3">
            <FieldPalette onAddField={handleAddField} />
          </div>

          {/* Zone principale */}
          <div className="col-span-12 lg:col-span-6">
            <Card title="Configuration du formulaire">
              <div className="space-y-4 mb-6">
                <Input
                  label="Nom du formulaire"
                  value={currentFormulaire.nom || ''}
                  onChange={(e) => updateCurrentFormulaire({ nom: e.target.value })}
                  placeholder="Entrez le nom du formulaire"
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={currentFormulaire.description || ''}
                    onChange={(e) => updateCurrentFormulaire({ description: e.target.value })}
                    placeholder="Description du formulaire (optionnel)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                  />
                </div>
              </div>

              {/* Onglets pour formulaire simple vs multi-étapes */}
              {isMultiStep && (
                <div className="flex gap-2 mb-4 border-b border-gray-200">
                  <button
                    onClick={() => setViewMode('fields')}
                    className={`px-4 py-2 font-medium transition-colors ${
                      viewMode === 'fields'
                        ? 'text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Liste des champs
                  </button>
                  <button
                    onClick={() => setViewMode('steps')}
                    className={`px-4 py-2 font-medium transition-colors ${
                      viewMode === 'steps'
                        ? 'text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Organisation par étapes
                  </button>
                </div>
              )}

              <div className="border-t border-gray-200 pt-6">
                {isMultiStep && viewMode === 'steps' ? (
                  <StepManager
                    etapes={currentFormulaire.structure_json.etapes || []}
                    champs={currentFormulaire.structure_json.champs}
                    onUpdateEtapes={(etapes) => {
                      updateCurrentFormulaire({
                        structure_json: {
                          ...currentFormulaire.structure_json,
                          etapes
                        }
                      });
                    }}
                  />
                ) : (
                  <>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Champs du formulaire</h3>
                    {currentFormulaire.structure_json.champs.length === 0 ? (
                      <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                        <p className="text-gray-600">
                          Aucun champ ajouté. Glissez des champs depuis la palette de gauche.
                        </p>
                      </div>
                    ) : (
                      <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
                        <SortableContext
                          items={currentFormulaire.structure_json.champs.map((_, i) => i)}
                          strategy={verticalListSortingStrategy}
                        >
                          <FieldList
                            fields={currentFormulaire.structure_json.champs}
                            selectedIndex={selectedFieldIndex}
                            onSelectField={setSelectedFieldIndex}
                            onDeleteField={removeChamp}
                          />
                        </SortableContext>
                      </DndContext>
                    )}
                  </>
                )}
              </div>
            </Card>
          </div>

          {/* Éditeur de champ */}
          <div className="col-span-12 lg:col-span-3">
            {selectedFieldIndex !== null && currentFormulaire.structure_json.champs[selectedFieldIndex] ? (
              <FieldEditor
                field={currentFormulaire.structure_json.champs[selectedFieldIndex]}
                onUpdateField={(updates: Partial<ChampFormulaire>) => updateChamp(selectedFieldIndex, updates)}
                onClose={() => setSelectedFieldIndex(null)}
              />
            ) : (
              <Card title="Propriétés du champ">
                <p className="text-sm text-gray-600 text-center py-8">
                  Sélectionnez un champ pour modifier ses propriétés
                </p>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
