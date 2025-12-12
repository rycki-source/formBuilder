import { apiClient } from './axios';

export interface DashboardStats {
  total_formulaires: number;
  formulaires_publies: number;
  formulaires_supprimes: number;
  total_soumissions: number;
  soumissions_validees: number;
  soumissions_en_attente: number;
  soumissions_rejetees: number;
  formulaires_recents: Array<{
    id: number;
    nom: string;
    description: string;
    est_publie: boolean;
    date_creation: string;
  }>;
}

export const dashboardApi = {
  getStats: async (): Promise<DashboardStats> => {
    const { data } = await apiClient.get('/dashboard/stats');
    return data;
  },
};
