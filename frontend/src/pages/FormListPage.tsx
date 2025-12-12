import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit, Trash2, Eye, Globe, GlobeLock, FileText } from 'lucide-react';
import { useFormBuilderStore } from '../store/formBuilderStore';
import { Card } from '../components/Card';
import { Button } from '../components/Button';

export const FormListPage = () => {
  const navigate = useNavigate();
  const { formulaires, fetchFormulaires, deleteFormulaire, publishFormulaire, unpublishFormulaire } = useFormBuilderStore();
  const [filter, setFilter] = useState<'all' | 'published' | 'draft'>('all');

  useEffect(() => {
    fetchFormulaires();
  }, [fetchFormulaires]);

  const filteredFormulaires = formulaires.filter((form) => {
    if (filter === 'published') return form.publie;
    if (filter === 'draft') return !form.publie;
    return true;
  });

  const handleDelete = async (id: string, nom: string) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer le formulaire "${nom}" ?`)) {
      try {
        await deleteFormulaire(id);
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      }
    }
  };

  const handleTogglePublish = async (id: string, isPublished: boolean) => {
    try {
      if (isPublished) {
        await unpublishFormulaire(id);
      } else {
        await publishFormulaire(id);
      }
    } catch (error) {
      console.error('Erreur lors de la publication:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Mes Formulaires</h1>
            <p className="text-gray-600">Gérez tous vos formulaires</p>
          </div>
          <div className="flex gap-3">
            <Button
              variant="secondary"
              onClick={() => navigate('/formulaires/dynamique')}
              className="flex items-center"
            >
              <span className="mr-2">📥</span>
              Importer référentiel
            </Button>
            <Button
              variant="primary"
              onClick={() => navigate('/formulaires/creer')}
            >
              <Plus className="w-5 h-5 mr-2" />
              Nouveau formulaire
            </Button>
          </div>
        </div>

        {/* Filtres */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Tous ({formulaires.length})
          </button>
          <button
            onClick={() => setFilter('published')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'published'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Publiés ({formulaires.filter(f => f.publie).length})
          </button>
          <button
            onClick={() => setFilter('draft')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'draft'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Brouillons ({formulaires.filter(f => !f.publie).length})
          </button>
        </div>

        {/* Liste des formulaires */}
        {filteredFormulaires.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <p className="text-gray-600 mb-4">Aucun formulaire trouvé</p>
              <Button variant="primary" onClick={() => navigate('/formulaires/creer')}>
                Créer un formulaire
              </Button>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredFormulaires.map((formulaire) => (
              <Card key={formulaire.id} className="hover:shadow-lg transition-shadow">
                <div className="space-y-4">
                  <div>
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-gray-900 text-lg line-clamp-2">
                        {formulaire.nom}
                      </h3>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium shrink-0 ml-2 ${
                          formulaire.publie
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {formulaire.publie ? 'Publié' : 'Brouillon'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {formulaire.description || 'Aucune description'}
                    </p>
                  </div>

                  <div className="text-sm text-gray-500">
                    <p>{formulaire.structure_json?.champs?.length || 0} champs</p>
                    {formulaire.date_creation && (
                      <p>Créé le {new Date(formulaire.date_creation).toLocaleDateString('fr-FR')}</p>
                    )}
                  </div>

                  <div className="flex items-center gap-2 pt-4 border-t border-gray-200">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => navigate(`/formulaires/${formulaire.id}`)}
                      title="Éditer"
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => navigate(`/formulaires/${formulaire.id}/preview`)}
                      title="Aperçu"
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => navigate(`/formulaires/${formulaire.id}/soumissions`)}
                      title="Soumissions"
                    >
                      <FileText className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTogglePublish(String(formulaire.id!), formulaire.publie)}
                      title={formulaire.publie ? 'Dépublier' : 'Publier'}
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
                      onClick={() => handleDelete(String(formulaire.id!), formulaire.nom)}
                      title="Supprimer"
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
