import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Plus, FileText, Users, CheckCircle, Clock, XCircle } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useFormBuilderStore } from '../store/formBuilderStore';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { dashboardApi, type DashboardStats } from '../api/dashboard';

export const DashboardPage = () => {
  const { t } = useTranslation();
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
      title: t('dashboard.totalForms'),
      value: dashboardStats.total_formulaires,
      icon: FileText,
      color: 'bg-blue-500',
    },
    {
      title: t('dashboard.publishedForms'),
      value: dashboardStats.formulaires_publies,
      icon: CheckCircle,
      color: 'bg-green-500',
    },
    {
      title: t('dashboard.deletedForms'),
      value: dashboardStats.formulaires_supprimes,
      icon: XCircle,
      color: 'bg-gray-500',
    },
    {
      title: t('dashboard.totalSubmissions'),
      value: dashboardStats.total_soumissions,
      icon: Users,
      color: 'bg-purple-500',
    },
    {
      title: t('dashboard.validatedSubmissions'),
      value: dashboardStats.soumissions_validees,
      icon: CheckCircle,
      color: 'bg-emerald-500',
    },
    {
      title: t('dashboard.pendingSubmissions'),
      value: dashboardStats.soumissions_en_attente,
      icon: Clock,
      color: 'bg-yellow-500',
    },
    {
      title: t('dashboard.rejectedSubmissions'),
      value: dashboardStats.soumissions_rejetees,
      icon: XCircle,
      color: 'bg-red-500',
    },
  ] : [];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {t('dashboard.welcome')}, {user?.username || user?.email}
          </h1>
          <p className="text-gray-600">
            {t('app.description')}
          </p>
        </div>

        {/* Actions rapides */}
        <div className="mb-8">
          <Link to="/formulaires/creer">
            <Button variant="primary" size="lg">
              <Plus className="w-5 h-5 mr-2" />
              {t('forms.createNew')}
            </Button>
          </Link>
        </div>

        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {loading ? (
            <div className="col-span-3 text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">{t('common.loading')}</p>
            </div>
          ) : stats.length === 0 ? (
            <div className="col-span-3 text-center py-12">
              <p className="text-gray-600">{t('dashboard.noStats')}</p>
            </div>
          ) : (
            stats.map((stat, index) => (
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
            ))
          )}
        </div>

        {/* Formulaires récents */}
        <Card title={t('dashboard.recentForms')}>
          {formulaires.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">{t('dashboard.noForms')}</p>
              <Link to="/formulaires/creer">
                <Button variant="primary">
                  {t('dashboard.createFirst')}
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
                        {formulaire.publie ? t('forms.published') : t('forms.draft')}
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
