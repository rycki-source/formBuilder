/**
 * Composant pour importer un référentiel de formulaire
 * Support: fichier local, URL distante, ou collage de texte
 */

/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState, useRef } from 'react';
import type { FormReferentiel } from '../types/referentiel.types';
import { parseFile, parseFromURL, parseReferentiel } from '../utils/parser';
import { validateReferentiel } from '../utils/referentielValidator';
import { Button } from '../../../components/Button';
import { Card } from '../../../components/Card';
import { apiClient } from '../../../api/axios';

export interface FormImporterProps {
  onImport: (referentiel: FormReferentiel) => void;
  onError?: (error: string) => void;
  allowedSources?: ('file' | 'url' | 'paste')[];
  validateSchema?: boolean;
  className?: string;
}

type Tab = 'file' | 'url' | 'paste';

const FormImporter: React.FC<FormImporterProps> = ({
  onImport,
  onError,
  allowedSources = ['file', 'url', 'paste'],
  validateSchema = true,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<Tab>(allowedSources[0] as Tab);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warnings, setWarnings] = useState<string[]>([]);

  // États pour chaque source
  const [url, setUrl] = useState('');
  const [pastedContent, setPastedContent] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Gestion des erreurs
  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    if (onError) {
      onError(errorMessage);
    }
  };

  // Import depuis un fichier
  const handleFileImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setWarnings([]);

    try {
      console.log('🔄 Début import fichier:', file.name);
      
      // Vérifier si c'est un fichier Excel
      const ext = file.name.split('.').pop()?.toLowerCase();
      if (ext === 'xlsx' || ext === 'xls') {
        console.log('📤 Envoi au backend...');
        
        // Envoyer au backend pour traitement
        const formData = new FormData();
        formData.append('file', file);

        const response = await apiClient.post('/referentiels/import/excel', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        console.log('📥 Réponse reçue:', response.data);

        if (!response.data || !response.data.referentiel) {
          console.error('❌ Réponse invalide:', response.data);
          handleError('Réponse invalide du serveur');
          setLoading(false);
          return;
        }

        const referentielData = response.data.referentiel;
        console.log('✅ Référentiel extrait:', referentielData);
        console.log('📊 Sections:', referentielData?.config?.sections?.length || 0);
      
        // Valider le référentiel
        if (validateSchema) {
          const validationResult = validateReferentiel(referentielData);

          if (!validationResult.isValid) {
            const errorMessages = validationResult.errors
              .map(e => `${e.path}: ${e.message}`)
              .join('\n');
            handleError(`Erreurs de validation:\n${errorMessages}`);
            setLoading(false);
            return;
          }

          if (validationResult.warnings.length > 0) {
            setWarnings(validationResult.warnings.map(w => `${w.path}: ${w.message}`));
          }
        }

        // Import réussi
        console.log('✅ Validation OK, appel de onImport');
        onImport(referentielData);
        console.log('✅ onImport appelé, fin du traitement');
        setLoading(false);
        return;
      }

      console.log('📄 Parsing fichier non-Excel...');
      // Parser le fichier (JSON, YAML, JS, TS)
      const parseResult = await parseFile(file);

      if (!parseResult.success || !parseResult.data) {
        handleError(parseResult.error || 'Erreur lors du parsing du fichier');
        return;
      }

      // Valider le référentiel
      if (validateSchema) {
        const validationResult = validateReferentiel(parseResult.data);

        if (!validationResult.isValid) {
          const errorMessages = validationResult.errors
            .map(e => `${e.path}: ${e.message}`)
            .join('\n');
          handleError(`Erreurs de validation:\n${errorMessages}`);
          return;
        }

        if (validationResult.warnings.length > 0) {
          setWarnings(validationResult.warnings.map(w => `${w.path}: ${w.message}`));
        }
      }

      // Import réussi
      console.log('✅ Import non-Excel réussi');
      onImport(parseResult.data);
    } catch (error: any) {
      console.error('❌ Erreur dans handleFileImport:', error);
      handleError(error.message || 'Erreur inconnue');
    } finally {
      console.log('🏁 Fin handleFileImport, setLoading(false)');
      setLoading(false);
    }
  };

  // Import depuis une URL
  const handleUrlImport = async () => {
    if (!url.trim()) {
      handleError('Veuillez entrer une URL');
      return;
    }

    setLoading(true);
    setError(null);
    setWarnings([]);

    try {
      // Parser depuis l'URL
      const parseResult = await parseFromURL(url);

      if (!parseResult.success || !parseResult.data) {
        handleError(parseResult.error || 'Erreur lors de la récupération depuis l\'URL');
        return;
      }

      // Valider le référentiel
      if (validateSchema) {
        const validationResult = validateReferentiel(parseResult.data);

        if (!validationResult.isValid) {
          const errorMessages = validationResult.errors
            .map(e => `${e.path}: ${e.message}`)
            .join('\n');
          handleError(`Erreurs de validation:\n${errorMessages}`);
          return;
        }

        if (validationResult.warnings.length > 0) {
          setWarnings(validationResult.warnings.map(w => `${w.path}: ${w.message}`));
        }
      }

      // Import réussi
      onImport(parseResult.data);
      setUrl(''); // Réinitialiser
    } catch (error: any) {
      handleError(error.message || 'Erreur inconnue');
    } finally {
      setLoading(false);
    }
  };

  // Import depuis le contenu collé
  const handlePasteImport = () => {
    if (!pastedContent.trim()) {
      handleError('Veuillez coller du contenu');
      return;
    }

    setLoading(true);
    setError(null);
    setWarnings([]);

    try {
      // Parser le contenu
      const parseResult = parseReferentiel(pastedContent);

      if (!parseResult.success || !parseResult.data) {
        handleError(parseResult.error || 'Erreur lors du parsing du contenu');
        return;
      }

      // Valider le référentiel
      if (validateSchema) {
        const validationResult = validateReferentiel(parseResult.data);

        if (!validationResult.isValid) {
          const errorMessages = validationResult.errors
            .map(e => `${e.path}: ${e.message}`)
            .join('\n');
          handleError(`Erreurs de validation:\n${errorMessages}`);
          return;
        }

        if (validationResult.warnings.length > 0) {
          setWarnings(validationResult.warnings.map(w => `${w.path}: ${w.message}`));
        }
      }

      // Import réussi
      onImport(parseResult.data);
      setPastedContent(''); // Réinitialiser
    } catch (error: any) {
      handleError(error.message || 'Erreur inconnue');
    } finally {
      setLoading(false);
    }
  };

  // Tabs
  const tabs = [
    { id: 'file' as Tab, label: '📁 Fichier', icon: '📁' },
    { id: 'url' as Tab, label: '🌐 URL', icon: '🌐' },
    { id: 'paste' as Tab, label: '📋 Coller', icon: '📋' }
  ].filter(tab => allowedSources.includes(tab.id));

  return (
    <Card className={`p-6 ${className}`}>
      <h2 className="text-2xl font-bold mb-4">Importer un Référentiel</h2>
      <p className="text-gray-600 mb-6">
        Importez un référentiel de formulaire depuis un fichier, une URL ou en collant le contenu.
        Formats supportés: JSON, YAML, JavaScript, TypeScript.
      </p>

      {/* Onglets */}
      <div className="flex border-b mb-6">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === tab.id
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Contenu des onglets */}
      <div className="min-h-[300px]">
        {/* Import depuis fichier */}
        {activeTab === 'file' && (
          <div className="space-y-4">
            <div className="border-2 border-dashed border-blue-300 rounded-lg p-10 text-center hover:border-blue-500 hover:bg-blue-50 transition-all">
              <input
                ref={fileInputRef}
                type="file"
                accept=".json,.yaml,.yml,.js,.ts,.xlsx,.xls"
                onChange={handleFileImport}
                className="hidden"
                aria-label="Importer un fichier de référentiel"
                disabled={loading}
              />
              <div className="space-y-4">
                <div className="text-7xl">📄</div>
                <div>
                  <p className="text-xl font-bold text-gray-900 mb-2">
                    Importer un référentiel
                  </p>
                  <p className="text-sm text-gray-600 mb-4">
                    Formats supportés : Excel, JSON, YAML, JavaScript ou TypeScript
                  </p>
                </div>
                <div className="flex flex-col items-center gap-3">
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={loading}
                    variant="primary"
                    className="text-base px-8 py-3 font-semibold"
                  >
                    {loading ? '⏳ Chargement...' : '📁 Choisir un fichier'}
                  </Button>
                  <p className="text-xs text-gray-500">
                    ou glissez-déposez un fichier ici
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Import depuis URL */}
        {activeTab === 'url' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                URL du référentiel
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/form-referentiel.json"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              />
              <p className="mt-2 text-sm text-gray-500">
                L'URL doit pointer vers un fichier JSON, YAML, JS ou TS accessible publiquement.
              </p>
            </div>
            <Button
              onClick={handleUrlImport}
              disabled={loading || !url.trim()}
              variant="primary"
            >
              {loading ? 'Chargement...' : 'Importer depuis l\'URL'}
            </Button>
          </div>
        )}

        {/* Import depuis contenu collé */}
        {activeTab === 'paste' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Collez le contenu du référentiel
              </label>
              <textarea
                value={pastedContent}
                onChange={(e) => setPastedContent(e.target.value)}
                placeholder="Collez ici le contenu JSON, YAML, JS ou TS..."
                rows={12}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                disabled={loading}
              />
              <p className="mt-2 text-sm text-gray-500">
                Le format sera détecté automatiquement.
              </p>
            </div>
            <Button
              onClick={handlePasteImport}
              disabled={loading || !pastedContent.trim()}
              variant="primary"
            >
              {loading ? 'Analyse...' : 'Importer le contenu'}
            </Button>
          </div>
        )}
      </div>

      {/* Avertissements */}
      {warnings.length > 0 && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
          <h4 className="font-semibold text-yellow-800 mb-2">⚠️ Avertissements</h4>
          <ul className="list-disc list-inside text-sm text-yellow-700 space-y-1">
            {warnings.map((warning, index) => (
              <li key={index}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Erreurs */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <h4 className="font-semibold text-red-800 mb-2">❌ Erreur</h4>
          <pre className="text-sm text-red-700 whitespace-pre-wrap">{error}</pre>
        </div>
      )}
    </Card>
  );
};

export default FormImporter;
