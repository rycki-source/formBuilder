import { apiClient } from './axios';
import type { Soumission, SoumissionCreate } from '../types';

export const soumissionsApi = {
  getAll: async (formulaireId?: string): Promise<Soumission[]> => {
    const params = formulaireId ? { formulaire_id: formulaireId } : {};
    const response = await apiClient.get('/soumissions', { params });
    return response.data;
  },

  getById: async (id: string): Promise<Soumission> => {
    const response = await apiClient.get(`/soumissions/${id}`);
    return response.data;
  },

  create: async (soumission: SoumissionCreate): Promise<Soumission> => {
    const response = await apiClient.post('/soumissions', soumission);
    return response.data;
  },

  updateStatus: async (id: string, statut: 'en_attente' | 'validee' | 'rejetee'): Promise<Soumission> => {
    const response = await apiClient.put(`/soumissions/${id}/statut`, { statut });
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/soumissions/${id}`);
  },
};
