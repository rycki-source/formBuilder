// Types pour l'authentification
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  statut: string;
  date_creation: string;
  derniere_connexion?: string;
}

// Types pour les formulaires
export interface ChampFormulaire {
  id?: string;
  label: string;
  type_champ: 'text' | 'email' | 'number' | 'date' | 'select' | 'textarea' | 'checkbox' | 'radio' | 'file' | 'button';
  placeholder?: string;
  obligatoire: boolean;
  ordre: number;
  options?: string[];
  validation?: Record<string, unknown>;
  buttonType?: 'submit' | 'reset' | 'button';
  buttonStyle?: 'primary' | 'secondary' | 'danger';
}

export type TypeStructurel = 'simple' | 'multi-etapes' | 'wizard' | 'integre' | 'modal';
export type TypeFonctionnel = 'contact' | 'inscription' | 'connexion' | 'commande' | 'commentaire' | 'candidature' | 'lead' | 'reservation' | 'personnalise';

export interface EtapeFormulaire {
  id: string;
  titre: string;
  description?: string;
  champs: ChampFormulaire[];
}

export interface Formulaire {
  id?: number;
  nom: string;
  description?: string;
  type_structurel: TypeStructurel;
  type_fonctionnel: TypeFonctionnel;
  structure_json: {
    champs: ChampFormulaire[];
    etapes?: EtapeFormulaire[];
  };
  version?: string;
  actif?: boolean;
  publie: boolean;
  date_creation?: string;
  date_modification?: string;
}

export interface FormulaireCreate {
  nom: string;
  description?: string;
  type_structurel: TypeStructurel;
  type_fonctionnel: TypeFonctionnel;
  structure_json: {
    champs: ChampFormulaire[];
    etapes?: EtapeFormulaire[];
  };
}

// Types pour les soumissions
export interface Soumission {
  id?: string;
  formulaire_id: string;
  reponses?: Record<string, unknown>;
  donnees: Record<string, unknown>;
  statut: 'en_attente' | 'validee' | 'rejetee';
  date_soumission: string;
  date_validation?: string;
  soumis_par?: string;
  utilisateur_id?: number;
}

export interface SoumissionCreate {
  formulaire_id: string;
  reponses?: Record<string, unknown>;
  donnees: Record<string, unknown>;
  statut?: 'en_attente' | 'validee' | 'rejetee';
}

// Types pour les référentiels
export interface Referentiel {
  id?: string;
  nom: string;
  type: string;
  donnees: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}
