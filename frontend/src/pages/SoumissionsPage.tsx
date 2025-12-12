import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle, XCircle, Clock, Download, Trash2 } from 'lucide-react';
import { soumissionsApi } from '../api/soumissions';
import { useFormBuilderStore } from '../store/formBuilderStore';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import type { Soumission } from '../types';

export const SoumissionsPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentFormulaire, fetchFormulaireById } = useFormBuilderStore();
  const [soumissions, setSoumissions] = useState<Soumission[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'en_attente' | 'validee' | 'rejetee'>('all');

  useEffect(() => {
    if (id) {
      fetchFormulaireById(id);
      loadSoumissions();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const loadSoumissions = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await soumissionsApi.getAll(id);
      setSoumissions(data);
    } catch (error) {
      console.error('Erreur lors du chargement des soumissions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (soumissionId: string, statut: 'en_attente' | 'validee' | 'rejetee') => {
    try {
      await soumissionsApi.updateStatus(soumissionId, statut);
      await loadSoumissions();
      
      // Message de confirmation selon le statut
      const messages = {
        'validee': '✓ Soumission validée avec succès',
        'rejetee': '✗ Soumission rejetée',
        'en_attente': '⏳ Soumission mise en attente'
      };
      alert(messages[statut] || 'Statut mis à jour');
    } catch (error) {
      console.error('Erreur lors de la mise à jour du statut:', error);
      alert('Erreur lors de la mise à jour du statut');
    }
  };

  const handleDelete = async (soumissionId: string) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette soumission ?')) return;
    
    try {
      await soumissionsApi.delete(soumissionId);
      await loadSoumissions();
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
      alert('Erreur lors de la suppression de la soumission');
    }
  };

  const handleExportExcel = async () => {
    const ids = filteredSoumissions
      .map(s => s.id)
      .filter((id): id is string => id !== undefined)
      .map(id => Number(id))
      .filter(id => !Number.isNaN(id));
    
    if (ids.length === 0) {
      alert('Aucune soumission à exporter');
      return;
    }

    try {
      const blob = await soumissionsApi.exportExcel(ids);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `soumissions_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Erreur lors de l\'export Excel:', error);
      alert('Erreur lors de l\'export Excel');
    }
  };

  const handleExportCSV = async () => {
    const ids = filteredSoumissions
      .map(s => s.id)
      .filter((id): id is string => id !== undefined)
      .map(id => Number(id))
      .filter(id => !Number.isNaN(id));
    
    if (ids.length === 0) {
      alert('Aucune soumission à exporter');
      return;
    }

    try {
      const blob = await soumissionsApi.exportCSV(ids);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `soumissions_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Erreur lors de l\'export CSV:', error);
      alert('Erreur lors de l\'export CSV');
    }
  };

  const handleExportJSON = async () => {
    const ids = filteredSoumissions
      .map(s => s.id)
      .filter((id): id is string => id !== undefined)
      .map(id => Number(id))
      .filter(id => !Number.isNaN(id));
    
    if (ids.length === 0) {
      alert('Aucune soumission à exporter');
      return;
    }

    try {
      const blob = await soumissionsApi.exportJSON(ids);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `soumissions_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Erreur lors de l\'export JSON:', error);
      alert('Erreur lors de l\'export JSON');
    }
  };

  const filteredSoumissions = soumissions.filter(s => {
    if (filter === 'all') return true;
    return s.statut.toLowerCase() === filter;
  });

  const getStatusBadge = (statut: string) => {
    const statusLower = statut.toLowerCase();
    switch (statusLower) {
      case 'validee':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            Validée
          </span>
        );
      case 'rejetee':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <XCircle className="w-3 h-3 mr-1" />
            Rejetée
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <Clock className="w-3 h-3 mr-1" />
            En attente
          </span>
        );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="outline" size="sm" onClick={() => navigate('/formulaires')}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Retour
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Soumissions</h1>
                <p className="text-sm text-gray-600">{currentFormulaire?.nom}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleExportExcel}>
                <Download className="w-4 h-4 mr-2" />
                Exporter Excel
              </Button>
              <Button variant="outline" onClick={handleExportCSV}>
                <Download className="w-4 h-4 mr-2" />
                Exporter CSV
              </Button>
              <Button variant="outline" onClick={handleExportJSON}>
                <Download className="w-4 h-4 mr-2" />
                Exporter JSON
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
            Toutes ({soumissions.length})
          </button>
          <button
            onClick={() => setFilter('en_attente')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'en_attente'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            En attente ({soumissions.filter(s => s.statut.toLowerCase() === 'en_attente' || s.statut.toLowerCase() === 'soumis').length})
          </button>
          <button
            onClick={() => setFilter('validee')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'validee'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Validées ({soumissions.filter(s => s.statut.toLowerCase() === 'validee').length})
          </button>
          <button
            onClick={() => setFilter('rejetee')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'rejetee'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Rejetées ({soumissions.filter(s => s.statut.toLowerCase() === 'rejetee').length})
          </button>
        </div>

        {/* Liste des soumissions */}
        {filteredSoumissions.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <p className="text-gray-600">Aucune soumission trouvée</p>
            </div>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredSoumissions.map((soumission) => (
              <Card key={soumission.id}>
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        {getStatusBadge(soumission.statut)}
                        <span className="text-sm text-gray-500">
                          {new Date(soumission.date_soumission).toLocaleString('fr-FR')}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                        {Object.entries(soumission.donnees).map(([key, value]) => (
                          <dl key={key}>
                            <dt className="text-sm font-medium text-gray-500">{key}</dt>
                            <dd className="mt-1 text-sm text-gray-900">
                              {typeof value === 'boolean' ? (value ? 'Oui' : 'Non') : String(value)}
                            </dd>
                          </dl>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 pt-4 border-t border-gray-200">
                    {soumission.statut.toLowerCase() !== 'validee' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleUpdateStatus(soumission.id!, 'validee')}
                      >
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Valider
                      </Button>
                    )}
                    {soumission.statut.toLowerCase() !== 'rejetee' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleUpdateStatus(soumission.id!, 'rejetee')}
                      >
                        <XCircle className="w-4 h-4 mr-1" />
                        Rejeter
                      </Button>
                    )}
                    {soumission.statut.toLowerCase() !== 'en_attente' && soumission.statut.toLowerCase() !== 'soumis' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleUpdateStatus(soumission.id!, 'en_attente')}
                      >
                        <Clock className="w-4 h-4 mr-1" />
                        En attente
                      </Button>
                    )}
                    <div className="flex-1" />
                    <Button
                      size="sm"
                      variant="danger"
                      onClick={() => handleDelete(soumission.id!)}
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
