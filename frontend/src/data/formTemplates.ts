import type { ChampFormulaire, TypeFonctionnel } from '../types';

export interface FormTemplate {
  type: TypeFonctionnel;
  nom: string;
  description: string;
  icon: string;
  champs: Omit<ChampFormulaire, 'id' | 'ordre'>[];
}

export const formTemplates: FormTemplate[] = [
  {
    type: 'contact',
    nom: 'Formulaire de Contact',
    description: 'Formulaire simple pour permettre aux visiteurs de vous contacter',
    icon: '📧',
    champs: [
      { label: 'Nom complet', type_champ: 'text', obligatoire: true, placeholder: 'Votre nom' },
      { label: 'Email', type_champ: 'email', obligatoire: true, placeholder: 'votre@email.com' },
      { label: 'Téléphone', type_champ: 'text', obligatoire: false, placeholder: '+33 6 12 34 56 78' },
      { label: 'Sujet', type_champ: 'select', obligatoire: true, options: ['Information', 'Support', 'Vente', 'Autre'] },
      { label: 'Message', type_champ: 'textarea', obligatoire: true, placeholder: 'Votre message...' },
      { label: 'Envoyer', type_champ: 'button', obligatoire: false, buttonType: 'submit', buttonStyle: 'primary' }
    ]
  },
  {
    type: 'inscription',
    nom: 'Formulaire d\'Inscription',
    description: 'Créer un compte utilisateur avec validation',
    icon: '👤',
    champs: [
      { label: 'Nom d\'utilisateur', type_champ: 'text', obligatoire: true, placeholder: 'Choisissez un nom d\'utilisateur' },
      { label: 'Email', type_champ: 'email', obligatoire: true, placeholder: 'votre@email.com' },
      { label: 'Mot de passe', type_champ: 'text', obligatoire: true, placeholder: 'Minimum 8 caractères' },
      { label: 'Confirmer le mot de passe', type_champ: 'text', obligatoire: true, placeholder: 'Retapez votre mot de passe' },
      { label: 'J\'accepte les conditions d\'utilisation', type_champ: 'checkbox', obligatoire: true },
      { label: 'S\'inscrire', type_champ: 'button', obligatoire: false, buttonType: 'submit', buttonStyle: 'primary' },
      { label: 'Annuler', type_champ: 'button', obligatoire: false, buttonType: 'reset', buttonStyle: 'secondary' }
    ]
  },
  {
    type: 'connexion',
    nom: 'Formulaire de Connexion',
    description: 'Authentification simple des utilisateurs',
    icon: '🔐',
    champs: [
      { label: 'Email ou nom d\'utilisateur', type_champ: 'text', obligatoire: true, placeholder: 'Votre identifiant' },
      { label: 'Mot de passe', type_champ: 'text', obligatoire: true, placeholder: 'Votre mot de passe' },
      { label: 'Se souvenir de moi', type_champ: 'checkbox', obligatoire: false },
      { label: 'Se connecter', type_champ: 'button', obligatoire: false, buttonType: 'submit', buttonStyle: 'primary' }
    ]
  },
  {
    type: 'commande',
    nom: 'Formulaire de Commande',
    description: 'Collecter les informations de paiement et d\'expédition',
    icon: '🛒',
    champs: [
      { label: 'Nom complet', type_champ: 'text', obligatoire: true },
      { label: 'Email', type_champ: 'email', obligatoire: true },
      { label: 'Téléphone', type_champ: 'text', obligatoire: true },
      { label: 'Adresse de livraison', type_champ: 'textarea', obligatoire: true },
      { label: 'Code postal', type_champ: 'text', obligatoire: true },
      { label: 'Ville', type_champ: 'text', obligatoire: true },
      { label: 'Pays', type_champ: 'select', obligatoire: true, options: ['France', 'Belgique', 'Suisse', 'Canada'] },
      { label: 'Mode de paiement', type_champ: 'radio', obligatoire: true, options: ['Carte bancaire', 'PayPal', 'Virement'] },
      { label: 'Commander', type_champ: 'button', obligatoire: false, buttonType: 'submit', buttonStyle: 'primary' }
    ]
  },
  {
    type: 'commentaire',
    nom: 'Formulaire de Feedback',
    description: 'Recueillir les avis et commentaires des utilisateurs',
    icon: '⭐',
    champs: [
      { label: 'Votre nom', type_champ: 'text', obligatoire: false },
      { label: 'Email', type_champ: 'email', obligatoire: true },
      { label: 'Note globale', type_champ: 'radio', obligatoire: true, options: ['⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'] },
      { label: 'Que pensez-vous de notre service ?', type_champ: 'textarea', obligatoire: true, placeholder: 'Partagez votre expérience...' },
      { label: 'Recommanderiez-vous notre service ?', type_champ: 'radio', obligatoire: true, options: ['Oui', 'Non', 'Peut-être'] },
      { label: 'Envoyer mon avis', type_champ: 'button', obligatoire: false, buttonType: 'submit', buttonStyle: 'primary' }
    ]
  },
  {
    type: 'candidature',
    nom: 'Formulaire de Candidature',
    description: 'Demandes d\'emploi ou d\'admission',
    icon: '📄',
    champs: [
      { label: 'Prénom', type_champ: 'text', obligatoire: true },
      { label: 'Nom', type_champ: 'text', obligatoire: true },
      { label: 'Email', type_champ: 'email', obligatoire: true },
      { label: 'Téléphone', type_champ: 'text', obligatoire: true },
      { label: 'Poste souhaité', type_champ: 'select', obligatoire: true, options: ['Développeur', 'Designer', 'Chef de projet', 'Marketing', 'Autre'] },
      { label: 'Années d\'expérience', type_champ: 'number', obligatoire: true },
      { label: 'CV (PDF)', type_champ: 'file', obligatoire: true },
      { label: 'Lettre de motivation', type_champ: 'textarea', obligatoire: true, placeholder: 'Présentez votre motivation...' },
      { label: 'Disponibilité', type_champ: 'select', obligatoire: true, options: ['Immédiate', '1 mois', '2 mois', '3+ mois'] },
      { label: 'Postuler', type_champ: 'button', obligatoire: false, buttonType: 'submit', buttonStyle: 'primary' }
    ]
  },
  {
    type: 'lead',
    nom: 'Génération de Leads',
    description: 'Capturer des prospects pour le marketing',
    icon: '🎯',
    champs: [
      { label: 'Prénom', type_champ: 'text', obligatoire: true },
      { label: 'Nom', type_champ: 'text', obligatoire: true },
      { label: 'Email professionnel', type_champ: 'email', obligatoire: true },
      { label: 'Entreprise', type_champ: 'text', obligatoire: true },
      { label: 'Poste', type_champ: 'text', obligatoire: false },
      { label: 'Téléphone', type_champ: 'text', obligatoire: false },
      { label: 'Taille de l\'entreprise', type_champ: 'select', obligatoire: true, options: ['1-10', '11-50', '51-200', '200+'] },
      { label: 'Intéressé par', type_champ: 'checkbox', obligatoire: false },
      { label: 'Télécharger le guide', type_champ: 'button', obligatoire: false, buttonType: 'submit', buttonStyle: 'primary' }
    ]
  },
  {
    type: 'reservation',
    nom: 'Formulaire de Réservation',
    description: 'Réserver un rendez-vous, une table, un service',
    icon: '📅',
    champs: [
      { label: 'Nom complet', type_champ: 'text', obligatoire: true },
      { label: 'Email', type_champ: 'email', obligatoire: true },
      { label: 'Téléphone', type_champ: 'text', obligatoire: true },
      { label: 'Date souhaitée', type_champ: 'date', obligatoire: true },
      { label: 'Heure', type_champ: 'select', obligatoire: true, options: ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00'] },
      { label: 'Nombre de personnes', type_champ: 'number', obligatoire: true },
      { label: 'Service', type_champ: 'select', obligatoire: true, options: ['Consultation', 'Rendez-vous', 'Démonstration', 'Autre'] },
      { label: 'Demandes spéciales', type_champ: 'textarea', obligatoire: false, placeholder: 'Informations supplémentaires...' },
      { label: 'Réserver', type_champ: 'button', obligatoire: false, buttonType: 'submit', buttonStyle: 'primary' }
    ]
  },
  {
    type: 'personnalise',
    nom: 'Formulaire Personnalisé',
    description: 'Créer un formulaire depuis zéro avec vos propres champs',
    icon: '✨',
    champs: []
  }
];
