import { create } from 'zustand';
import { formulairesApi } from '../api/formulaires';
import type { Formulaire, FormulaireCreate, ChampFormulaire } from '../types';

interface FormBuilderState {
  formulaires: Formulaire[];
  currentFormulaire: Formulaire | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions pour la liste des formulaires
  fetchFormulaires: () => Promise<void>;
  fetchFormulaireById: (id: string) => Promise<void>;
  createFormulaire: (formulaire: FormulaireCreate) => Promise<Formulaire>;
  updateFormulaire: (id: string, formulaire: Partial<FormulaireCreate>) => Promise<void>;
  deleteFormulaire: (id: string) => Promise<void>;
  publishFormulaire: (id: string) => Promise<void>;
  unpublishFormulaire: (id: string) => Promise<void>;
  
  // Actions pour l'édition du formulaire courant
  setCurrentFormulaire: (formulaire: Formulaire | null) => void;
  updateCurrentFormulaire: (updates: Partial<Formulaire>) => void;
  initializeFromTemplate: (typeStructurel: string, typeFonctionnel: string, champs: ChampFormulaire[]) => void;
  addChamp: (champ: ChampFormulaire) => void;
  updateChamp: (index: number, champ: Partial<ChampFormulaire>) => void;
  removeChamp: (index: number) => void;
  reorderChamps: (startIndex: number, endIndex: number) => void;
  
  clearError: () => void;
}

export const useFormBuilderStore = create<FormBuilderState>((set, get) => ({
  formulaires: [],
  currentFormulaire: null,
  isLoading: false,
  error: null,

  fetchFormulaires: async () => {
    set({ isLoading: true, error: null });
    try {
      const formulaires = await formulairesApi.getAll();
      set({ formulaires, isLoading: false });
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      set({ 
        error: err.response?.data?.detail || 'Erreur lors du chargement des formulaires',
        isLoading: false,
      });
    }
  },

  fetchFormulaireById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const formulaire = await formulairesApi.getById(id);
      set({ currentFormulaire: formulaire, isLoading: false });
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      set({ 
        error: err.response?.data?.detail || 'Erreur lors du chargement du formulaire',
        isLoading: false,
      });
    }
  },

  createFormulaire: async (formulaire: FormulaireCreate) => {
    set({ isLoading: true, error: null });
    try {
      const newFormulaire = await formulairesApi.create(formulaire);
      set({ 
        formulaires: [...get().formulaires, newFormulaire],
        currentFormulaire: newFormulaire,
        isLoading: false,
      });
      return newFormulaire;
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      set({ 
        error: err.response?.data?.detail || 'Erreur lors de la création du formulaire',
        isLoading: false,
      });
      throw error;
    }
  },

  updateFormulaire: async (id: string, formulaire: Partial<FormulaireCreate>) => {
    set({ isLoading: true, error: null });
    try {
      const updatedFormulaire = await formulairesApi.update(id, formulaire);
      set({ 
        formulaires: get().formulaires.map(f => String(f.id) === String(id) ? updatedFormulaire : f),
        currentFormulaire: updatedFormulaire,
        isLoading: false,
      });
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      set({ 
        error: err.response?.data?.detail || 'Erreur lors de la mise à jour du formulaire',
        isLoading: false,
      });
      throw error;
    }
  },

  deleteFormulaire: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await formulairesApi.delete(id);
      set({ 
        formulaires: get().formulaires.filter(f => String(f.id) !== String(id)),
        isLoading: false,
      });
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      set({ 
        error: err.response?.data?.detail || 'Erreur lors de la suppression du formulaire',
        isLoading: false,
      });
      throw error;
    }
  },

  publishFormulaire: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const updatedFormulaire = await formulairesApi.publish(id);
      set({ 
        formulaires: get().formulaires.map(f => String(f.id) === String(id) ? updatedFormulaire : f),
        currentFormulaire: updatedFormulaire,
        isLoading: false,
      });
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      set({ 
        error: err.response?.data?.detail || 'Erreur lors de la publication du formulaire',
        isLoading: false,
      });
      throw error;
    }
  },

  unpublishFormulaire: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const updatedFormulaire = await formulairesApi.unpublish(id);
      set({ 
        formulaires: get().formulaires.map(f => String(f.id) === String(id) ? updatedFormulaire : f),
        currentFormulaire: updatedFormulaire,
        isLoading: false,
      });
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      set({ 
        error: err.response?.data?.detail || 'Erreur lors de la dépublication du formulaire',
        isLoading: false,
      });
      throw error;
    }
  },

  setCurrentFormulaire: (formulaire: Formulaire | null) => {
    set({ currentFormulaire: formulaire });
  },

  updateCurrentFormulaire: (updates: Partial<Formulaire>) => {
    const current = get().currentFormulaire;
    if (current) {
      set({ currentFormulaire: { ...current, ...updates } });
    }
  },

  initializeFromTemplate: (typeStructurel: string, typeFonctionnel: string, champs: ChampFormulaire[]) => {
    const champsWithOrder = champs.map((champ, index) => ({
      ...champ,
      id: `field-${Date.now()}-${index}`,
      ordre: index,
    }));
    
    const isMultiStep = typeStructurel === 'multi-etapes' || typeStructurel === 'wizard';
    const etapes = isMultiStep ? [
      {
        id: 'step-1',
        titre: 'Étape 1',
        description: 'Première étape du formulaire',
        champs: champsWithOrder.slice(0, Math.ceil(champsWithOrder.length / 2))
      },
      {
        id: 'step-2',
        titre: 'Étape 2',
        description: 'Deuxième étape du formulaire',
        champs: champsWithOrder.slice(Math.ceil(champsWithOrder.length / 2))
      }
    ] : undefined;
    
    const structureJson = isMultiStep 
      ? { champs: [], etapes }
      : { champs: champsWithOrder, etapes: undefined };
    
    set({
      currentFormulaire: {
        nom: '',
        description: '',
        type_structurel: typeStructurel as 'simple' | 'multi-etapes' | 'wizard' | 'integre' | 'modal',
        type_fonctionnel: typeFonctionnel as 'contact' | 'inscription' | 'connexion' | 'commande' | 'commentaire' | 'candidature' | 'lead' | 'reservation' | 'personnalise',
        publie: false,
        structure_json: structureJson,
      },
    });
  },

  addChamp: (champ: ChampFormulaire) => {
    const current = get().currentFormulaire;
    if (current) {
      const champs = current.structure_json?.champs || [];
      set({ 
        currentFormulaire: { 
          ...current, 
          structure_json: {
            ...current.structure_json,
            champs: [...champs, champ],
          },
        },
      });
    }
  },

  updateChamp: (index: number, champ: Partial<ChampFormulaire>) => {
    const current = get().currentFormulaire;
    if (current && current.structure_json?.champs) {
      const newChamps = [...current.structure_json.champs];
      newChamps[index] = { ...newChamps[index], ...champ };
      set({ 
        currentFormulaire: { 
          ...current, 
          structure_json: {
            ...current.structure_json,
            champs: newChamps,
          },
        },
      });
    }
  },

  removeChamp: (index: number) => {
    const current = get().currentFormulaire;
    if (current && current.structure_json?.champs) {
      set({ 
        currentFormulaire: { 
          ...current, 
          structure_json: {
            ...current.structure_json,
            champs: current.structure_json.champs.filter((_, i) => i !== index),
          },
        },
      });
    }
  },

  reorderChamps: (startIndex: number, endIndex: number) => {
    const current = get().currentFormulaire;
    if (current && current.structure_json?.champs) {
      const newChamps = [...current.structure_json.champs];
      const [removed] = newChamps.splice(startIndex, 1);
      newChamps.splice(endIndex, 0, removed);
      
      // Mettre à jour l'ordre
      newChamps.forEach((champ, index) => {
        champ.ordre = index;
      });
      
      set({ 
        currentFormulaire: { 
          ...current, 
          structure_json: {
            ...current.structure_json,
            champs: newChamps,
          },
        },
      });
    }
  },

  clearError: () => set({ error: null }),
}));
