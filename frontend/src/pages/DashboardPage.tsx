import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, FileText, Users, CheckCircle, Clock, XCircle } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useSimpleTranslation } from '../hooks/useSimpleTranslation';
import { useFormBuilderStore } from '../store/formBuilderStore';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { dashboardApi, type DashboardStats } from '../api/dashboard';

export const DashboardPage = () => {
  const { translate } = useSimpleTranslation();
  const { user } = useAuth();
  const { formulaires, fetchFormulaires } = useFormBuilderStore();
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        console.log('🔄 Début chargement dashboard...');
        setLoading(true);
        
        console.log('📋 Chargement formulaires...');
        await fetchFormulaires();
        
        console.log('📊 Appel API stats...');
        const stats = await dashboardApi.getStats();
        console.log('✅ Stats reçues:', stats);
        setDashboardStats(stats);
      } catch (error) {
        console.error('❌ Erreur lors du chargement des statistiques:', error);
        console.error('Détails:', error);
      } finally {
        console.log('✅ Fin chargement, loading=false');
        setLoading(false);
      }
    };
    loadData();
  }, [fetchFormulaires]);

  const stats = dashboardStats ? [
    {
      title: translate('Total Formulaires', 'Total Forms'),
      value: dashboardStats.total_formulaires,
      icon: FileText,
      color: 'bg-blue-500',
    },
    {
      title: translate('Formulaires publiés', 'Published Forms'),
      value: dashboardStats.formulaires_publies,
      icon: CheckCircle,
      color: 'bg-green-500',
    },
    {
      title: translate('Formulaires supprimés', 'Deleted Forms'),
      value: dashboardStats.formulaires_supprimes,
      icon: XCircle,
      color: 'bg-gray-500',
    },
    {
      title: translate('Total Soumissions', 'Total Submissions'),
      value: dashboardStats.total_soumissions,
      icon: Users,
      color: 'bg-purple-500',
    },
    {
      title: translate('Soumissions validées', 'Validated Submissions'),
      value: dashboardStats.soumissions_validees,
      icon: CheckCircle,
      color: 'bg-emerald-500',
    },
    {
      title: translate('Soumissions en attente', 'Pending Submissions'),
      value: dashboardStats.soumissions_en_attente,
      icon: Clock,
      color: 'bg-yellow-500',
    },
    {
      title: translate('Soumissions rejetées', 'Rejected Submissions'),
      value: dashboardStats.soumissions_rejetees,
      icon: XCircle,
      color: 'bg-red-500',
    },
  ] : [];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="w-full max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        {/* Header */}
        <div className="mb-4 sm:mb-6 md:mb-8">
          <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 mb-2">
            {translate('Bienvenue', 'Welcome')}, {user?.username || user?.email}
          </h1>
          <p className="text-sm sm:text-base text-gray-600 mb-4 sm:mb-8">
            {translate('Plateforme de génération dynamique de formulaires', 'Dynamic form generation platform')}
          </p>
        </div>

        {/* Actions rapides */}
        <div className="mb-6 sm:mb-8">
          <Link to="/formulaires/creer" className="block sm:inline-block">
            <Button variant="primary" size="lg" className="w-full sm:w-auto">
              <Plus className="w-5 h-5 mr-2" />
              {translate('Créer un formulaire', 'Create a form')}
            </Button>
          </Link>
        </div>

        {/* Statistiques */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4 md:gap-6 mb-4 sm:mb-6 md:mb-8">
          {loading ? (
            <div className="col-span-full text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">{translate('Chargement...', 'Loading...')}</p>
            </div>
          ) : stats.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-600">{translate('Aucune statistique disponible', 'No statistics available')}</p>
            </div>
          ) : (
            stats.map((stat, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow p-3 sm:p-4">
                <div className="flex items-center gap-3">
                  <div className={`${stat.color} p-2 sm:p-3 rounded-lg shrink-0`}>
                    <stat.icon className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="ml-3 sm:ml-4 min-w-0">
                    <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{stat.title}</p>
                    <p className="text-xl sm:text-2xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>

        {/* Formulaires récents */}
        <div className="bg-white rounded-lg shadow-sm p-3 sm:p-4 md:p-6">
          <h2 className="text-base sm:text-lg md:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">
            {translate('Formulaires récents', 'Recent Forms')}
          </h2>
          {formulaires.length === 0 ? (
            <div className="text-center py-8 sm:py-12">
              <FileText className="w-10 h-10 sm:w-12 sm:h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-sm sm:text-base text-gray-600 mb-4">{translate('Aucun formulaire créé', 'No forms created')}</p>
              <Link to="/formulaires/creer">
                <Button variant="primary" className="w-full sm:w-auto">
                  {translate('Créer votre premier formulaire', 'Create your first form')}
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-3 sm:space-y-4">
              {formulaires.slice(0, 5).map((formulaire) => (
                <Link
                  key={formulaire.id}
                  to={`/formulaires/${formulaire.id}`}
                  className="block p-3 sm:p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <h3 className="font-semibold text-gray-900 truncate text-sm sm:text-base">{formulaire.nom}</h3>
                      <p className="text-xs sm:text-sm text-gray-600 line-clamp-2">{formulaire.description}</p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <span
                        className={`px-2 sm:px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap ${
                          formulaire.publie
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {formulaire.publie ? translate('Publié', 'Published') : translate('Brouillon', 'Draft')}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
