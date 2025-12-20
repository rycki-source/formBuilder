import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSimpleTranslation } from '../hooks/useSimpleTranslation';
import { Plus, Edit, Trash2, Eye, Globe, GlobeLock, FileText } from 'lucide-react';
import { useFormBuilderStore } from '../store/formBuilderStore';
import { Card } from '../components/Card';
import { Button } from '../components/Button';

export const FormListPage = () => {
  const { translate } = useSimpleTranslation();
  const navigate = useNavigate();
  const { formulaires, fetchFormulaires, deleteFormulaire, publishFormulaire, unpublishFormulaire } = useFormBuilderStore();
  const [filter, setFilter] = useState<'all' | 'published' | 'draft'>('all');

  useEffect(() => {
    fetchFormulaires();
  }, [fetchFormulaires]);

  const filteredFormulaires = formulaires.filter((form) => {
    // Ignorer les formulaires sans ID
    if (!form.id) return false;
    
    if (filter === 'published') return form.publie;
    if (filter === 'draft') return !form.publie;
    return true;
  });

  const handleDelete = async (id: number, nom: string) => {
    if (window.confirm(`${translate('Voulez-vous vraiment supprimer', 'Do you really want to delete')} "${nom}" ?`)) {
      try {
        await deleteFormulaire(String(id));
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      }
    }
  };

  const handleTogglePublish = async (id: number, isPublished: boolean) => {
    try {
      if (isPublished) {
        await unpublishFormulaire(String(id));
      } else {
        await publishFormulaire(String(id));
      }
    } catch (error) {
      console.error('Erreur lors de la publication:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="w-full max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 sm:gap-4 mb-4 sm:mb-6 md:mb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-1 sm:mb-2">{translate('Mes formulaires', 'My Forms')}</h1>
            <p className="text-sm sm:text-base text-gray-600">{translate('Gérez vos formulaires', 'Manage your forms')}</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
            <Button
              variant="secondary"
              onClick={() => navigate('/formulaires/dynamique')}
              className="flex items-center justify-center w-full sm:w-auto text-sm sm:text-base"
            >
              <span className="mr-2">📥</span>
              <span className="hidden lg:inline">{translate('Importer un référentiel', 'Import Referential')}</span>
              <span className="lg:hidden">{translate('Importer', 'Import')}</span>
            </Button>
            <Button
              variant="primary"
              onClick={() => navigate('/formulaires/creer')}
              className="w-full sm:w-auto"
            >
              <Plus className="w-5 h-5 sm:mr-2" />
              <span className="hidden sm:inline">{translate('Nouveau formulaire', 'New Form')}</span>
            </Button>
          </div>
        </div>

        {/* Filtres */}
        <div className="flex gap-2 sm:gap-4 mb-4 sm:mb-6 overflow-x-auto pb-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 sm:px-4 py-2 rounded-lg text-sm sm:text-base font-medium transition-colors whitespace-nowrap ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            {translate('Tous', 'All')} ({formulaires.length})
          </button>
          <button
            onClick={() => setFilter('published')}
            className={`px-3 sm:px-4 py-2 rounded-lg text-sm sm:text-base font-medium transition-colors whitespace-nowrap ${
              filter === 'published'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            {translate('Publiés', 'Published')} ({formulaires.filter(f => f.publie).length})
          </button>
          <button
            onClick={() => setFilter('draft')}
            className={`px-3 sm:px-4 py-2 rounded-lg text-sm sm:text-base font-medium transition-colors whitespace-nowrap ${
              filter === 'draft'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            {translate('Brouillons', 'Drafts')} ({formulaires.filter(f => !f.publie).length})
          </button>
        </div>

        {/* Liste des formulaires */}
        {filteredFormulaires.length === 0 ? (
          <Card>
            <div className="text-center py-8 sm:py-12">
              <p className="text-sm sm:text-base text-gray-600 mb-4">{translate('Aucun formulaire trouvé', 'No forms found')}</p>
              <Button variant="primary" onClick={() => navigate('/formulaires/creer')} className="w-full sm:w-auto">
                {translate('Créer un formulaire', 'Create Form')}
              </Button>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
            {filteredFormulaires.map((formulaire) => (
              <Card key={formulaire.id} className="hover:shadow-lg transition-shadow p-3 sm:p-4 md:p-6">
                <div className="space-y-3 sm:space-y-4">
                  <div>
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-gray-900 text-base sm:text-lg line-clamp-2">
                        {formulaire.nom}
                      </h3>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium shrink-0 ml-2 ${
                          formulaire.publie
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {formulaire.publie ? translate('Publié', 'Published') : translate('Brouillon', 'Draft')}
                      </span>
                    </div>
                    <p className="text-xs sm:text-sm text-gray-600 line-clamp-2">
                      {formulaire.description || translate('Aucune description', 'No description')}
                    </p>
                  </div>

                  <div className="text-xs sm:text-sm text-gray-500">
                    <p>{formulaire.structure_json?.champs?.length || 0} {translate('champs', 'fields')}</p>
                    {formulaire.date_creation && (
                      <p>{translate('Créé le', 'Created on')} {new Date(formulaire.date_creation).toLocaleDateString('fr-FR')}</p>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 pt-2 sm:pt-3 border-t border-gray-200">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => navigate(`/formulaires/${formulaire.id}`)}
                      title={translate('Éditer', 'Edit')}
                      className="flex-1 sm:flex-none min-w-0 text-xs sm:text-sm px-2 sm:px-3"
                    >
                      <Edit className="w-3 h-3 sm:w-4 sm:h-4 shrink-0" />
                      <span className="ml-1 sm:hidden text-xs">{translate('Éditer', 'Edit')}</span>
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => navigate(`/formulaires/${formulaire.id}/preview`)}
                      title={translate('Aperçu', 'Preview')}
                      className="flex-1 sm:flex-none min-w-0 text-xs sm:text-sm px-2 sm:px-3"
                    >
                      <Eye className="w-3 h-3 sm:w-4 sm:h-4 shrink-0" />
                      <span className="ml-1 sm:hidden text-xs">{translate('Voir', 'View')}</span>
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => navigate(`/formulaires/${formulaire.id}/soumissions`)}
                      title={translate('Soumissions', 'Submissions')}
                      className="flex-1 sm:flex-none"
                    >
                      <FileText className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTogglePublish(formulaire.id!, formulaire.publie)}
                      title={formulaire.publie ? translate('Dépublier', 'Unpublish') : translate('Publier', 'Publish')}
                    >
                      {formulaire.publie ? (
                        <GlobeLock className="w-4 h-4" />
                      ) : (
                        <Globe className="w-4 h-4" />
                      )}
                    </Button>
                    <Button
                      size="sm"
                      variant="danger"
                      onClick={() => handleDelete(formulaire.id!, formulaire.nom)}
                      title={translate('Supprimer', 'Delete')}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
