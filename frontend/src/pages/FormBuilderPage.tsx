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
import { ErrorAlert } from '../components/ErrorAlert';
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
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

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
    // Réinitialiser les messages
    setError(null);
    setSuccess(null);

    if (!currentFormulaire?.nom?.trim()) {
      setError('⚠️ NOM_REQUIS\n\nLe nom du formulaire est obligatoire.\n\n➜ Veuillez saisir un nom pour le formulaire');
      return;
    }

    if (!currentFormulaire?.structure_json?.champs || currentFormulaire.structure_json.champs.length === 0) {
      setError('⚠️ CHAMPS_REQUIS\n\nLe formulaire doit contenir au moins un champ.\n\n➜ Veuillez ajouter au moins un champ au formulaire');
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
        setSuccess('✅ Formulaire mis à jour avec succès');
        setTimeout(() => navigate('/formulaires'), 2000);
        return true;
      } else {
        await createFormulaire(formData);
        setSuccess('✅ Formulaire créé avec succès');
        setTimeout(() => navigate('/formulaires'), 2000);
        return true;
      }
    } catch (error: any) {
      console.error('Erreur lors de la sauvegarde:', error);
      
      // Extraire le message d'erreur structuré
      const errorData = error?.response?.data;
      let errorMessage = '❌ ERREUR_SAUVEGARDE\n\nErreur lors de la sauvegarde du formulaire\n\n➜ Veuillez réessayer';
      
      if (errorData && typeof errorData === 'object') {
        if (errorData.error && errorData.message && errorData.action) {
          errorMessage = `❌ ${errorData.error}\n\n${errorData.message}\n\n➜ ${errorData.action}`;
        } else if (errorData.message) {
          errorMessage = `❌ ${errorData.message}`;
        } else if (errorData.detail) {
          const detail = typeof errorData.detail === 'string' 
            ? errorData.detail 
            : JSON.stringify(errorData.detail, null, 2);
          errorMessage = `❌ ${detail}`;
        }
      }
      
      setError(errorMessage);
      return false;
    }
  };

  const handlePreview = async () => {
    if (id && id !== 'nouveau') {
      navigate(`/formulaires/${id}/preview`);
    } else {
      // Proposer de sauvegarder d'abord
      const shouldSave = window.confirm('Le formulaire doit être enregistré avant de voir l\'aperçu. Voulez-vous l\'enregistrer maintenant ?');
      if (shouldSave) {
        await handleSave();
        // La navigation sera faite après la sauvegarde réussie
      }
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
        {/* Messages d'erreur et de succès */}
        {error && (
          <div className="mb-6">
            <ErrorAlert error={error} type="error" onClose={() => setError(null)} />
          </div>
        )}
        {success && (
          <div className="mb-6">
            <ErrorAlert error={success} type="info" onClose={() => setSuccess(null)} />
          </div>
        )}

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
                
                {/* Configuration Webhook */}
                <div className="border-t border-gray-200 pt-4 mt-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-gray-900">🔗 Intégration Webhook</h3>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={currentFormulaire.webhook_enabled || false}
                        onChange={(e) => updateCurrentFormulaire({ webhook_enabled: e.target.checked })}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">Activer</span>
                    </label>
                  </div>
                  
                  {currentFormulaire.webhook_enabled && (
                    <div className="space-y-3 bg-blue-50 p-3 rounded-lg">
                      <Input
                        label="URL de webhook"
                        type="url"
                        value={currentFormulaire.webhook_url || ''}
                        onChange={(e) => updateCurrentFormulaire({ webhook_url: e.target.value })}
                        placeholder="https://votre-site.com/api/webhook"
                      />
                      <Input
                        label="Secret (optionnel)"
                        type="password"
                        value={currentFormulaire.webhook_secret || ''}
                        onChange={(e) => updateCurrentFormulaire({ webhook_secret: e.target.value })}
                        placeholder="Clé secrète pour sécuriser le webhook"
                      />
                      <Input
                        label="Nombre de tentatives"
                        type="number"
                        min="1"
                        max="10"
                        value={currentFormulaire.webhook_retry_count || 3}
                        onChange={(e) => updateCurrentFormulaire({ webhook_retry_count: parseInt(e.target.value) || 3 })}
                      />
                      <p className="text-xs text-gray-600">
                        💡 Les soumissions seront automatiquement envoyées à cette URL
                      </p>
                    </div>
                  )}
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
