import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, X, Download, FileText, Code } from 'lucide-react';
import { useFormBuilderStore } from '../store/formBuilderStore';
import { soumissionsApi } from '../api/soumissions';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { Input } from '../components/Input';
import { MultiStepFormPreview } from '../components/MultiStepFormPreview';
import type { ChampFormulaire, EtapeFormulaire } from '../types';
import { apiClient } from '../api/axios';

export const FormPreviewPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentFormulaire, fetchFormulaireById } = useFormBuilderStore();
  const [formData, setFormData] = useState<Record<string, unknown>>({});
  const [showModal, setShowModal] = useState(false);
  const [showEmbedCode, setShowEmbedCode] = useState(false);
  const [embedCode, setEmbedCode] = useState('');

  useEffect(() => {
    if (id) {
      fetchFormulaireById(id);
    }
  }, [id, fetchFormulaireById]);

  const handleInputChange = (fieldLabel: string, value: unknown) => {
    setFormData(prev => ({ ...prev, [fieldLabel]: value }));
  };

  const handleSubmit = async (data?: Record<string, unknown>) => {
    const submitData = data || formData;
    
    if (!id) {
      alert('Erreur: ID du formulaire non trouvé');
      return;
    }

    try {
      await soumissionsApi.create({
        formulaire_id: id,
        donnees: submitData
      });
      
      alert('Formulaire soumis avec succès !');
      setFormData({}); // Réinitialiser le formulaire
      
      if (currentFormulaire?.type_structurel === 'modal') {
        setShowModal(false);
      }
    } catch (error) {
      console.error('Erreur lors de la soumission:', error);
      alert('Erreur lors de la soumission du formulaire');
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation des champs obligatoires
    let requiredFields: ChampFormulaire[] = [];
    
    if (normalizedChamps.length > 0) {
      // Formulaire simple
      requiredFields = normalizedChamps.filter(f => f.obligatoire) || [];
    } else if (normalizedEtapes.length > 0) {
      // Formulaire multi-étapes
      normalizedEtapes.forEach((etape: EtapeFormulaire) => {
        if (etape.champs) {
          requiredFields = [...requiredFields, ...etape.champs.filter((f: ChampFormulaire) => f.obligatoire)];
        }
      });
    }
    
    const missingFields = requiredFields.filter(f => !formData[f.label]);
    
    if (missingFields.length > 0) {
      alert(`Veuillez remplir les champs obligatoires : ${missingFields.map(f => f.label).join(', ')}`);
      return;
    }

    handleSubmit();
  };

  const handleDownloadHTML = async () => {
    if (!currentFormulaire) return;
    
    try {
      const response = await apiClient.get(`/formulaires/${id}/html`, {
        responseType: 'text'
      });
      
      // Créer un blob et télécharger
      const blob = new Blob([response.data], { type: 'text/html' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `formulaire_${currentFormulaire.nom.replace(/\s+/g, '_')}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Erreur lors du téléchargement HTML:', error);
      alert('Erreur lors du téléchargement du HTML');
    }
  };

  const handleDownloadPDF = async () => {
    if (!currentFormulaire) return;
    
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      alert('Vous devez être connecté pour télécharger le PDF');
      navigate('/login');
      return;
    }
    
    // Méthode 1: Téléchargement avec fetch
    try {
      const response = await fetch(`http://localhost:8000/api/v1/formulaires/${id}/pdf`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          alert('Session expirée. Veuillez vous reconnecter.');
          localStorage.removeItem('access_token');
          navigate('/login');
          return;
        }
        throw new Error(`Erreur HTTP: ${response.status}`);
      }
      
      const blob = await response.blob();
      
      if (blob.size === 0) {
        throw new Error('Le PDF généré est vide');
      }
      
      // Créer l'URL et télécharger
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `formulaire_${currentFormulaire.nom.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      
      setTimeout(() => {
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }, 100);
      
    } catch (error) {
      console.error('Erreur téléchargement PDF:', error);
      
      // Méthode 2 (fallback): Ouvrir dans un nouvel onglet
      console.log('Tentative méthode alternative...');
      const pdfUrl = `http://localhost:8000/api/v1/formulaires/${id}/pdf`;
      const newWindow = window.open(pdfUrl, '_blank');
      
      if (!newWindow) {
        alert('Impossible d\'ouvrir le PDF. Veuillez autoriser les pop-ups ou vérifier votre connexion.');
      }
    }
  };

  const handleGetEmbedCode = async () => {
    if (!currentFormulaire) return;
    
    try {
      const response = await apiClient.get(`/formulaires/${id}/embed`, {
        responseType: 'text'
      });
      
      setEmbedCode(response.data);
      setShowEmbedCode(true);
    } catch (error) {
      console.error('Erreur lors de la récupération du code:', error);
      alert('Erreur lors de la récupération du code embarquable');
    }
  };

  const handleCopyEmbedCode = () => {
    navigator.clipboard.writeText(embedCode);
    alert('✅ Code copié dans le presse-papier !');
  };

  const renderField = (field: ChampFormulaire) => {
    const commonProps = {
      label: field.label,
      placeholder: field.placeholder,
      required: field.obligatoire,
    };

    switch (field.type_champ) {
      case 'text':
      case 'email':
        return (
          <Input
            key={field.label}
            {...commonProps}
            type={field.type_champ}
            value={(formData[field.label] as string) || ''}
            onChange={(e) => handleInputChange(field.label, e.target.value)}
          />
        );

      case 'number':
        return (
          <Input
            key={field.label}
            {...commonProps}
            type="number"
            value={(formData[field.label] as string) || ''}
            onChange={(e) => handleInputChange(field.label, e.target.value)}
          />
        );

      case 'date':
        return (
          <Input
            key={field.label}
            {...commonProps}
            type="date"
            value={(formData[field.label] as string) || ''}
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
              value={(formData[field.label] as string) || ''}
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
              value={(formData[field.label] as string) || ''}
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
              checked={(formData[field.label] as boolean) || false}
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

      case 'button': {
        const buttonClasses = {
          primary: 'bg-blue-600 text-white hover:bg-blue-700',
          secondary: 'bg-gray-600 text-white hover:bg-gray-700',
          danger: 'bg-red-600 text-white hover:bg-red-700'
        };
        return (
          <div key={field.label} className="flex justify-center">
            <button
              type={field.buttonType || 'button'}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${buttonClasses[field.buttonStyle || 'primary']}`}
            >
              {field.label}
            </button>
          </div>
        );
      }

      case 'geolocation': {
        const GeolocationField = React.lazy(() => import('../components/GeolocationField'));
        return (
          <React.Suspense key={field.label} fallback={<div>Chargement...</div>}>
            <GeolocationField
              value={formData[field.label] as { latitude: number; longitude: number; accuracy?: number }}
              onChange={(value) => handleInputChange(field.label, value)}
              label={field.label}
              required={field.obligatoire}
            />
          </React.Suspense>
        );
      }

      case 'signature': {
        const SignatureField = React.lazy(() => import('../components/SignatureField'));
        return (
          <React.Suspense key={field.label} fallback={<div>Chargement...</div>}>
            <SignatureField
              value={formData[field.label] as string}
              onChange={(value) => handleInputChange(field.label, value)}
              label={field.label}
              required={field.obligatoire}
            />
          </React.Suspense>
        );
      }

      default:
        return null;
    }
  };

  if (!currentFormulaire) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Chargement...</div>
      </div>
    );
  }

  // Normalisation de la structure pour supporter différents formats
  const structureJson = currentFormulaire.structure_json as Record<string, unknown>;
  
  // Support de différents formats de structure
  const normalizedChamps: ChampFormulaire[] = (structureJson?.champs as ChampFormulaire[]) || 
    (structureJson?.sections ? (structureJson.sections as Array<{ champs?: ChampFormulaire[] }>).flatMap((section) => section.champs || []) : []);
  
  const normalizedEtapes: EtapeFormulaire[] = (structureJson?.etapes as EtapeFormulaire[]) || [];

  const isMultiStep = currentFormulaire.type_structurel === 'multi-etapes' || currentFormulaire.type_structurel === 'wizard';
  const isModal = currentFormulaire.type_structurel === 'modal';
  const etapes: EtapeFormulaire[] = normalizedEtapes;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col gap-4">
            {/* Ligne 1: Bouton retour et titre */}
            <div className="flex items-center justify-between">
              <Button variant="outline" size="sm" onClick={() => navigate(`/formulaires/${id}`)}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Retour à l'éditeur
              </Button>
              <div className="flex items-center gap-3">
                <h1 className="text-xl font-bold text-gray-900">Aperçu du formulaire</h1>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">
                  {currentFormulaire.type_structurel}
                </span>
              </div>
            </div>
            
            {/* Ligne 2: Boutons d'export */}
            <div className="flex items-center justify-center gap-3 pb-2">
              <Button variant="primary" size="sm" onClick={handleGetEmbedCode}>
                <Code className="w-4 h-4 mr-2" />
                Obtenir le code d'intégration
              </Button>
              <Button variant="outline" size="sm" onClick={handleDownloadHTML}>
                <FileText className="w-4 h-4 mr-2" />
                Télécharger HTML
              </Button>
              <Button variant="outline" size="sm" onClick={handleDownloadPDF}>
                <Download className="w-4 h-4 mr-2" />
                Télécharger PDF
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Modal pour afficher le code embarquable */}
      {showEmbedCode && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Code d'intégration</h2>
              <button
                onClick={() => setShowEmbedCode(false)}
                className="text-gray-400 hover:text-gray-600"
                aria-label="Fermer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Comment intégrer ce formulaire ?
                </h3>
                <p className="text-gray-600 mb-4">
                  Copiez ce code HTML et collez-le dans votre site web. Le formulaire enverra automatiquement 
                  les données à votre API FormBuilder.
                </p>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <p className="text-sm text-blue-800">
                    <strong>Note :</strong> Assurez-vous que votre API est accessible depuis votre site web 
                    (configurez CORS si nécessaire).
                  </p>
                </div>
              </div>

              <div className="relative">
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{embedCode}</code>
                </pre>
                
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleCopyEmbedCode}
                  className="absolute top-4 right-4"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Copier le code
                </Button>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Exemple d'intégration
                </h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <pre className="text-sm text-gray-800 overflow-x-auto">
{`<!DOCTYPE html>
<html>
<head>
    <title>Ma Page</title>
</head>
<body>
    <h1>Mon Site Web</h1>
    
    <!-- Collez le code du formulaire ici -->
    ${embedCode.substring(0, 100)}...
    
    <!-- Fin du code du formulaire -->
</body>
</html>`}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Mode Modal - Bouton pour ouvrir */}
        {isModal && !showModal && (
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">Ce formulaire s'affichera dans une fenêtre modale</p>
            <Button variant="primary" onClick={() => setShowModal(true)}>
              Ouvrir le formulaire
            </Button>
          </div>
        )}

        {/* Affichage Modal */}
        {isModal && showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900">{currentFormulaire.nom}</h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                  aria-label="Fermer le modal"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="p-6">
                {currentFormulaire.description && (
                  <p className="text-gray-600 mb-6">{currentFormulaire.description}</p>
                )}
                <form onSubmit={handleFormSubmit} className="space-y-6">
                  {normalizedChamps.map((field) => renderField(field))}
                  <div className="flex justify-end pt-4">
                    <Button type="submit" variant="primary">
                      <Send className="w-4 h-4 mr-2" />
                      Soumettre
                    </Button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Mode Multi-étapes/Wizard */}
        {!isModal && isMultiStep && etapes.length > 0 && (
          <MultiStepFormPreview
            etapes={etapes}
            onSubmit={handleSubmit}
          />
        )}

        {/* Mode Simple/Intégré */}
        {!isModal && !isMultiStep && (
          <Card>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{currentFormulaire.nom}</h2>
              {currentFormulaire.description && (
                <p className="text-gray-600">{currentFormulaire.description}</p>
              )}
            </div>

            <form onSubmit={handleFormSubmit} className="space-y-6">
              {normalizedChamps.map((field) => renderField(field))}

              <div className="flex justify-end pt-6 border-t border-gray-200">
                <Button type="submit" variant="primary">
                  <Send className="w-4 h-4 mr-2" />
                  Soumettre
                </Button>
              </div>
            </form>
          </Card>
        )}
      </div>
    </div>
  );
};
