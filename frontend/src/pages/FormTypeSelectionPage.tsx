import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { ArrowRight, Grid, List, Zap, Monitor, MessageSquare } from 'lucide-react';
import { formTemplates } from '../data/formTemplates';
import type { TypeStructurel, TypeFonctionnel } from '../types';

const structuralTypes: { value: TypeStructurel; label: string; description: string; icon: typeof Grid }[] = [
  { value: 'simple', label: 'Simple (Une page)', description: 'Tous les champs sur une seule page', icon: Grid },
  { value: 'multi-etapes', label: 'Multi-étapes', description: 'Formulaire divisé en plusieurs étapes avec progression', icon: List },
  { value: 'wizard', label: 'Assistant (Wizard)', description: 'Guide l\'utilisateur étape par étape', icon: Zap },
  { value: 'integre', label: 'Intégré', description: 'Formulaire intégré dans une page ou section', icon: Monitor },
  { value: 'modal', label: 'Pop-up / Modal', description: 'Apparaît dans une fenêtre au-dessus du contenu', icon: MessageSquare },
];

export const FormTypeSelectionPage = () => {
  const navigate = useNavigate();
  const [selectedStructural, setSelectedStructural] = useState<TypeStructurel>('simple');
  const [selectedFunctional, setSelectedFunctional] = useState<TypeFonctionnel | null>(null);

  const handleContinue = () => {
    if (selectedFunctional) {
      const template = formTemplates.find(t => t.type === selectedFunctional);
      navigate('/formulaires/nouveau', { 
        state: { 
          typeStructurel: selectedStructural,
          typeFonctionnel: selectedFunctional,
          template 
        } 
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Créer un nouveau formulaire</h1>
          <p className="mt-2 text-gray-600">Choisissez le type de formulaire que vous souhaitez créer</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Option Import Référentiel */}
          <Card className="bg-linear-to-r from-purple-50 to-blue-50 border-2 border-purple-200">
            <div className="flex items-center justify-between p-2">
              <div className="flex-1">
                <h3 className="text-lg font-bold text-gray-900 mb-2 flex items-center">
                  <span className="text-2xl mr-3">🚀</span>
                  Créer à partir d'un référentiel
                </h3>
                <p className="text-sm text-gray-700 mb-3">
                  Importez un fichier de configuration (Excel, JSON, YAML) pour générer automatiquement 
                  un formulaire complet avec validation, conditions et champs calculés.
                </p>
                <div className="flex gap-2 flex-wrap text-xs text-gray-600">
                  <span className="bg-white px-3 py-1 rounded-full">✓ Validation automatique</span>
                  <span className="bg-white px-3 py-1 rounded-full">✓ Champs conditionnels</span>
                  <span className="bg-white px-3 py-1 rounded-full">✓ Calculs dynamiques</span>
                </div>
              </div>
              <div className="ml-4">
                <Button
                  variant="primary"
                  onClick={() => navigate('/formulaires/dynamique')}
                  className="px-6 py-3 text-base font-semibold whitespace-nowrap"
                >
                  📥 Importer référentiel
                </Button>
              </div>
            </div>
          </Card>

          <div className="relative">
            <div className="absolute inset-0 flex items-center" aria-hidden="true">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center">
              <span className="bg-gray-50 px-4 text-sm text-gray-500 font-medium">OU créer manuellement</span>
            </div>
          </div>

          {/* Étape 1: Type Structurel */}
          <Card title="Étape 1 : Choisissez la structure">
            <p className="text-sm text-gray-600 mb-6">
              Comment souhaitez-vous présenter votre formulaire ?
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {structuralTypes.map((type) => (
                <button
                  key={type.value}
                  onClick={() => setSelectedStructural(type.value)}
                  className={`p-4 border-2 rounded-lg text-left transition-all hover:shadow-md ${
                    selectedStructural === type.value
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-300 bg-white hover:border-blue-400'
                  }`}
                >
                  <type.icon className={`w-8 h-8 mb-3 ${
                    selectedStructural === type.value ? 'text-blue-600' : 'text-gray-600'
                  }`} />
                  <h3 className="font-semibold text-gray-900 mb-1">{type.label}</h3>
                  <p className="text-xs text-gray-600">{type.description}</p>
                </button>
              ))}
            </div>
          </Card>

          {/* Étape 2: Type Fonctionnel */}
          <Card title="Étape 2 : Sélectionnez le type de formulaire">
            <p className="text-sm text-gray-600 mb-6">
              Quel est l'objectif de votre formulaire ?
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {formTemplates.map((template) => (
                <button
                  key={template.type}
                  onClick={() => setSelectedFunctional(template.type)}
                  className={`p-6 border-2 rounded-lg text-left transition-all hover:shadow-lg ${
                    selectedFunctional === template.type
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-300 bg-white hover:border-blue-400'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <span className="text-4xl">{template.icon}</span>
                    {selectedFunctional === template.type && (
                      <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </div>
                  <h3 className="font-bold text-gray-900 mb-2">{template.nom}</h3>
                  <p className="text-sm text-gray-600">{template.description}</p>
                  {template.champs.length > 0 && (
                    <p className="text-xs text-blue-600 mt-2">
                      {template.champs.length} champs prédéfinis
                    </p>
                  )}
                </button>
              ))}
            </div>
          </Card>

          {/* Bouton Continuer */}
          <div className="flex justify-end gap-4">
            <Button variant="secondary" onClick={() => navigate('/formulaires')}>
              Annuler
            </Button>
            <Button
              variant="primary"
              onClick={handleContinue}
              disabled={!selectedFunctional}
            >
              Continuer
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
