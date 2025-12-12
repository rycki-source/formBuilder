/**
 * Page de démonstration pour les formulaires dynamiques
 * Permet d'importer un référentiel et de prévisualiser le formulaire généré
 */

/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import FormImporter from '../features/DynamicForm/components/FormImporter';
import DynamicForm from '../features/DynamicForm/components/DynamicForm';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import type { FormReferentiel } from '../features/DynamicForm/types/referentiel.types';

// Exemples de référentiels
import basicFormExample from '../features/DynamicForm/examples/basic-form.json';
import advancedFormExample from '../features/DynamicForm/examples/advanced-form.json';

const DynamicFormPage: React.FC = () => {
  const navigate = useNavigate();
  const [referentiel, setReferentiel] = useState<FormReferentiel | null>(null);
  const [showImporter, setShowImporter] = useState(true);
  const [submittedData, setSubmittedData] = useState<any>(null);

  // Handler pour l'import du référentiel
  const handleImport = (importedReferentiel: FormReferentiel) => {
    console.log('🎯 handleImport appelé avec:', importedReferentiel);
    console.log('🔍 Sections disponibles:', importedReferentiel?.config?.sections);
    console.log('🔍 Nombre de sections:', importedReferentiel?.config?.sections?.length || 0);
    
    setReferentiel(importedReferentiel);
    setShowImporter(false);
    setSubmittedData(null);
    
    console.log('✅ État mis à jour - showImporter:', false, 'referentiel:', importedReferentiel);
  };

  // Handler pour la soumission du formulaire
  const handleSubmit = async (values: Record<string, any>) => {
    console.log('Formulaire soumis:', values);
    setSubmittedData(values);
    alert('Formulaire soumis avec succès ! Consultez la console pour voir les données.');
  };

  // Charger un exemple
  const loadExample = (type: 'basic' | 'advanced') => {
    const example = type === 'basic' ? basicFormExample : advancedFormExample;
    setReferentiel(example as FormReferentiel);
    setShowImporter(false);
    setSubmittedData(null);
  };

  // Réinitialiser
  const handleReset = () => {
    setReferentiel(null);
    setShowImporter(true);
    setSubmittedData(null);
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto py-8 px-4">
        {/* En-tête */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Formulaires Dynamiques
          </h1>
          <p className="text-gray-600 mt-2">
            Importez un référentiel de configuration (Excel, JSON, YAML) pour générer automatiquement un formulaire complet
            avec validation, conditions et champs calculés.
          </p>
        </div>

        {/* Boutons d'action */}
        <div className="mb-6 flex flex-wrap gap-3">
          {!showImporter && !referentiel && (
            <Button onClick={() => setShowImporter(true)} variant="primary" className="font-semibold">
              Importer un référentiel
            </Button>
          )}
          
          {!showImporter && referentiel && (
            <Button onClick={() => setShowImporter(true)} variant="secondary">
             Importer un nouveau référentiel
            </Button>
          )}
          
          {referentiel && (
            <Button onClick={handleReset} variant="secondary">
              Réinitialiser
            </Button>
          )}

          <Button onClick={() => loadExample('basic')} variant="secondary">
            Charger exemple simple
          </Button>

          <Button onClick={() => loadExample('advanced')} variant="secondary">
            Charger exemple avancé
          </Button>

          <Button onClick={() => navigate('/formulaires')} variant="secondary">
            ← Retour aux formulaires
          </Button>
        </div>

        {/* Message de bienvenue */}
        {!showImporter && !referentiel && (
          <Card className="p-8 mb-6 bg-linear-to-r from-blue-50 to-indigo-50 border-2 border-blue-200">
            <div className="text-center space-y-4">
              <div className="text-6xl">🚀</div>
              <h2 className="text-2xl font-bold text-gray-900">
                Commencez avec les formulaires dynamiques
              </h2>
              <p className="text-gray-700 max-w-2xl mx-auto">
                Importez un fichier de référentiel pour générer instantanément un formulaire complet
                avec validation, conditions et champs calculés.
              </p>
              <div className="flex justify-center gap-4 pt-4">
                <Button onClick={() => setShowImporter(true)} variant="primary" className="px-8 py-3 text-lg font-semibold">
                  📥 Importer mon référentiel
                </Button>
                <Button onClick={() => loadExample('basic')} variant="secondary" className="px-8 py-3 text-lg">
                  👀 Voir un exemple
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Importeur */}
        {showImporter && !referentiel && (
          <FormImporter
            onImport={handleImport}
            onError={(error) => console.error('Erreur d\'import:', error)}
            allowedSources={['file', 'url', 'paste']}
            validateSchema={true}
          />
        )}

        {/* Informations sur le référentiel chargé */}
        {referentiel && !showImporter && (
          <Card className="p-6 mb-6">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  {referentiel.metadata.name}
                </h2>
                {referentiel.metadata.description && (
                  <p className="text-gray-600 mt-1">
                    {referentiel.metadata.description}
                  </p>
                )}
                <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-500">
                  <span>Version: {referentiel.version}</span>
                  {referentiel.metadata.author && (
                    <span>Auteur: {referentiel.metadata.author}</span>
                  )}
                  {referentiel.metadata.tags && (
                    <span>
                      Tags: {referentiel.metadata.tags.join(', ')}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => {
                    const json = JSON.stringify(referentiel, null, 2);
                    navigator.clipboard.writeText(json);
                    alert('Référentiel copié dans le presse-papiers !');
                  }}
                  variant="secondary"
                  className="text-sm"
                >
                  📋 Copier
                </Button>
                <Button
                  onClick={() => {
                    const json = JSON.stringify(referentiel, null, 2);
                    const blob = new Blob([json], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${referentiel.config.id}.json`;
                    a.click();
                  }}
                  variant="secondary"
                  className="text-sm"
                >
                  💾 Télécharger
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Formulaire dynamique */}
        {referentiel && !showImporter && (
          <DynamicForm
            referentiel={referentiel}
            onSubmit={handleSubmit}
            showSubmitButton={true}
            showCancelButton={true}
            onCancel={handleReset}
          />
        )}

        {/* Données soumises */}
        {submittedData && (
          <Card className="p-6 mt-6">
            <h3 className="text-lg font-bold mb-3">Données soumises</h3>
            <pre className="bg-gray-50 p-4 rounded-md overflow-auto text-sm">
              {JSON.stringify(submittedData, null, 2)}
            </pre>
          </Card>
        )}

        {/* Documentation */}
        {!referentiel && !showImporter && (
          <Card className="p-6 mt-6">
            <h3 className="text-lg font-bold mb-3">📚 Documentation</h3>
            <div className="space-y-4 text-sm">
              <div>
                <h4 className="font-semibold mb-2">Formats supportés</h4>
                <ul className="list-disc list-inside text-gray-700 space-y-1">
                  <li>Excel (.xlsx, .xls) - avec structure de colonnes prédéfinie</li>
                  <li>JSON (.json)</li>
                  <li>YAML (.yaml, .yml)</li>
                  <li>JavaScript (.js)</li>
                  <li>TypeScript (.ts)</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Fonctionnalités</h4>
                <ul className="list-disc list-inside text-gray-700 space-y-1">
                  <li>Validation complète des champs (required, pattern, min/max, custom)</li>
                  <li>Conditions d'affichage dynamiques (show/hide selon valeurs)</li>
                  <li>Champs calculés automatiquement</li>
                  <li>Layouts flexibles (grid, flex, tabs, accordion)</li>
                  <li>Sauvegarde automatique (localStorage)</li>
                  <li>Support multi-sections et groupes de champs</li>
                  <li>Validateurs personnalisés</li>
                  <li>Messages d'erreur personnalisables</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Types de champs</h4>
                <ul className="list-disc list-inside text-gray-700 space-y-1">
                  <li>Texte: text, textarea, email, password, tel, url</li>
                  <li>Numériques: number, range</li>
                  <li>Date/Heure: date, datetime-local, time, month, week</li>
                  <li>Sélection: select, multiselect, radio, checkbox, switch</li>
                  <li>Autres: file, color, hidden</li>
                </ul>
              </div>
            </div>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default DynamicFormPage;
