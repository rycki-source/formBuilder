/**
 * Client API pour la gestion des référentiels de formulaires dynamiques
 */

import { apiClient as api } from './axios';
import type { FormReferentiel } from '../features/DynamicForm/types/referentiel.types';

// Types pour les réponses API
export interface ReferentielMetadata {
  name: string;
  description?: string;
  author?: string;
  tags?: string[];
  documentation_url?: string;
}

export interface ReferentielResponse {
  id: number;
  ref_id: string;
  version: string;
  metadata: ReferentielMetadata;
  config: FormReferentiel['config'];
  source_type: string;
  custom_validators?: Record<string, string>;
  custom_components?: Record<string, string>;
  tags?: string[];
  is_template: boolean;
  is_active: boolean;
  source_file?: string;
  created_at: string;
  updated_at?: string;
  personne_import_id: number;
}

export interface ReferentielListResponse {
  items: ReferentielResponse[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ReferentielImportResponse {
  success: boolean;
  message: string;
  referentiel: ReferentielResponse;
  warnings: string[];
}

export interface ReferentielCreateRequest {
  version: string;
  metadata: ReferentielMetadata;
  config: FormReferentiel['config'];
  source_type?: string;
  custom_validators?: Record<string, string>;
  custom_components?: Record<string, string>;
  tags?: string[];
  is_template?: boolean;
  is_active?: boolean;
}

export interface ReferentielUpdateRequest {
  version?: string;
  metadata?: ReferentielMetadata;
  config?: FormReferentiel['config'];
  custom_validators?: Record<string, string>;
  custom_components?: Record<string, string>;
  tags?: string[];
  is_template?: boolean;
  is_active?: boolean;
}

export interface ReferentielListParams {
  is_template?: boolean;
  is_active?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface ReferentielImportTextRequest {
  source_type: 'json' | 'yaml';
  content: string;
  save_as_template?: boolean;
}

/**
 * Convertir une réponse API en FormReferentiel
 */
export function convertToFormReferentiel(response: ReferentielResponse): FormReferentiel {
  return {
    version: response.version,
    metadata: response.metadata,
    config: response.config,
  };
}

/**
 * API Client pour les référentiels
 */
export const referentielsAPI = {
  /**
   * Créer un nouveau référentiel
   */
  async create(data: ReferentielCreateRequest): Promise<ReferentielResponse> {
    const response = await api.post<ReferentielResponse>('/referentiels/', data);
    return response.data;
  },

  /**
   * Lister les référentiels
   */
  async list(params?: ReferentielListParams): Promise<ReferentielListResponse> {
    const response = await api.get<ReferentielListResponse>('/referentiels/', { params });
    return response.data;
  },

  /**
   * Lister uniquement les templates publics
   */
  async listTemplates(params?: { page?: number; page_size?: number; search?: string }): Promise<ReferentielListResponse> {
    const response = await api.get<ReferentielListResponse>('/referentiels/templates', { params });
    return response.data;
  },

  /**
   * Récupérer un référentiel par ID
   */
  async get(id: number): Promise<ReferentielResponse> {
    const response = await api.get<ReferentielResponse>(`/referentiels/${id}`);
    return response.data;
  },

  /**
   * Récupérer un référentiel par ref_id
   */
  async getByRefId(refId: string): Promise<ReferentielResponse> {
    const response = await api.get<ReferentielResponse>(`/referentiels/by-ref-id/${refId}`);
    return response.data;
  },

  /**
   * Mettre à jour un référentiel
   */
  async update(id: number, data: ReferentielUpdateRequest): Promise<ReferentielResponse> {
    const response = await api.put<ReferentielResponse>(`/referentiels/${id}`, data);
    return response.data;
  },

  /**
   * Supprimer un référentiel
   */
  async delete(id: number): Promise<void> {
    await api.delete(`/referentiels/${id}`);
  },

  /**
   * Importer un référentiel depuis un fichier Excel
   */
  async importExcel(file: File, saveAsTemplate: boolean = false): Promise<ReferentielImportResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<ReferentielImportResponse>(
      `/referentiels/import/excel?save_as_template=${saveAsTemplate}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Importer un référentiel depuis un fichier JSON
   */
  async importJson(file: File, saveAsTemplate: boolean = false): Promise<ReferentielImportResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<ReferentielImportResponse>(
      `/referentiels/import/json?save_as_template=${saveAsTemplate}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Importer un référentiel depuis du texte (JSON/YAML collé)
   */
  async importText(data: ReferentielImportTextRequest): Promise<ReferentielImportResponse> {
    const response = await api.post<ReferentielImportResponse>('/referentiels/import/text', data);
    return response.data;
  },

  /**
   * Exporter un référentiel
   */
  async export(id: number, format: 'json' | 'yaml' = 'json'): Promise<ReferentielResponse> {
    const response = await api.post<ReferentielResponse>(`/referentiels/${id}/export?format=${format}`);
    return response.data;
  },

  /**
   * Télécharger un référentiel sous forme de fichier
   */
  async download(id: number, format: 'json' | 'yaml' = 'json'): Promise<void> {
    const data = await this.export(id, format);
    const referentiel = convertToFormReferentiel(data);
    
    const blob = new Blob(
      [JSON.stringify(referentiel, null, 2)],
      { type: 'application/json' }
    );
    
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `referentiel-${data.ref_id}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  /**
   * Charger un référentiel et le convertir en FormReferentiel
   */
  async load(id: number): Promise<FormReferentiel> {
    const response = await this.get(id);
    return convertToFormReferentiel(response);
  },

  /**
   * Charger un référentiel par ref_id et le convertir en FormReferentiel
   */
  async loadByRefId(refId: string): Promise<FormReferentiel> {
    const response = await this.getByRefId(refId);
    return convertToFormReferentiel(response);
  },
};

export default referentielsAPI;
