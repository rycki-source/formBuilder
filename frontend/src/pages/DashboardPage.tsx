import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, FileText, Users, CheckCircle } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useFormBuilderStore } from '../store/formBuilderStore';
import { Card } from '../components/Card';
import { Button } from '../components/Button';

export const DashboardPage = () => {
  const { user } = useAuth();
  const { formulaires, fetchFormulaires } = useFormBuilderStore();

  useEffect(() => {
    fetchFormulaires();
  }, [fetchFormulaires]);

  const stats = [
    {
      title: 'Total Formulaires',
      value: formulaires.length,
      icon: FileText,
      color: 'bg-blue-500',
    },
    {
      title: 'Formulaires Publiés',
      value: formulaires.filter(f => f.publie).length,
      icon: CheckCircle,
      color: 'bg-green-500',
    },
    {
      title: 'Soumissions',
      value: 0, // À implémenter
      icon: Users,
      color: 'bg-purple-500',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Bienvenue, {user?.username || user?.email}
          </h1>
          <p className="text-gray-600">
            Gérez vos formulaires et consultez les statistiques
          </p>
        </div>

        {/* Actions rapides */}
        <div className="mb-8">
          <Link to="/formulaires/creer">
            <Button variant="primary" size="lg">
              <Plus className="w-5 h-5 mr-2" />
              Créer un nouveau formulaire
            </Button>
          </Link>
        </div>

        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <div className="flex items-center">
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Formulaires récents */}
        <Card title="Formulaires récents">
          {formulaires.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">Aucun formulaire créé</p>
              <Link to="/formulaires/creer">
                <Button variant="primary">
                  Créer votre premier formulaire
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {formulaires.slice(0, 5).map((formulaire) => (
                <Link
                  key={formulaire.id}
                  to={`/formulaires/${formulaire.id}`}
                  className="block p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900">{formulaire.nom}</h3>
                      <p className="text-sm text-gray-600">{formulaire.description}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          formulaire.publie
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {formulaire.publie ? 'Publié' : 'Brouillon'}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};
