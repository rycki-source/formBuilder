import { apiClient } from './axios';
import type { Formulaire, FormulaireCreate } from '../types';

export const formulairesApi = {
  getAll: async (): Promise<Formulaire[]> => {
    const response = await apiClient.get('/formulaires/user');
    return response.data;
  },

  getById: async (id: number | string): Promise<Formulaire> => {
    const response = await apiClient.get(`/formulaires/${id}`);
    return response.data;
  },

  create: async (formulaire: FormulaireCreate): Promise<Formulaire> => {
    const response = await apiClient.post('/formulaires', formulaire);
    return response.data;
  },

  update: async (id: number | string, formulaire: Partial<FormulaireCreate>): Promise<Formulaire> => {
    const response = await apiClient.put(`/formulaires/${id}`, formulaire);
    return response.data;
  },

  delete: async (id: number | string): Promise<void> => {
    await apiClient.delete(`/formulaires/${id}`);
  },

  publish: async (id: number | string): Promise<Formulaire> => {
    const response = await apiClient.post(`/formulaires/${id}/publish`);
    return response.data;
  },

  unpublish: async (id: number | string): Promise<Formulaire> => {
    const response = await apiClient.put(`/formulaires/${id}`, { publie: false });
    return response.data;
  },
};
