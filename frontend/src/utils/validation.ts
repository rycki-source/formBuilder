/**
 * Utilitaires de validation côté frontend
 * Validation stricte synchronisée avec le backend
 */

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export interface FieldValidationResult {
  [fieldName: string]: ValidationResult;
}

/**
 * Validateur de mot de passe strict
 */
export class PasswordValidator {
  /**
   * Valide un mot de passe selon les règles strictes
   * Règles synchronisées avec le backend:
   * - 8-128 caractères
   * - Au moins 1 majuscule, 1 minuscule, 1 chiffre, 1 caractère spécial
   * - Pas d'espaces en début/fin
   * - Pas de séquences faibles
   */
  static validatePassword(password: string): ValidationResult {
    const result: ValidationResult = { isValid: true, errors: [] };
    
    if (!password) {
      result.errors.push("Le mot de passe est requis");
      result.isValid = false;
      return result;
    }
    
    // Longueur
    if (password.length < 8) {
      result.errors.push("Le mot de passe doit contenir au moins 8 caractères");
    }
    if (password.length > 128) {
      result.errors.push("Le mot de passe ne peut pas dépasser 128 caractères");
    }
    
    // Espaces en début/fin
    if (password !== password.trim()) {
      result.errors.push("Le mot de passe ne peut pas commencer ou finir par un espace");
    }
    
    // Majuscules
    if (!/[A-Z]/.test(password)) {
      result.errors.push("Le mot de passe doit contenir au moins une majuscule");
    }
    
    // Minuscules
    if (!/[a-z]/.test(password)) {
      result.errors.push("Le mot de passe doit contenir au moins une minuscule");
    }
    
    // Chiffres
    if (!/[0-9]/.test(password)) {
      result.errors.push("Le mot de passe doit contenir au moins un chiffre");
    }
    
    // Caractères spéciaux
    if (!/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(password)) {
      result.errors.push("Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*()_+-=[]{}|;:,.<>?)");
    }
    
    // Séquences faibles
    if (this.hasWeakSequences(password)) {
      result.errors.push("Le mot de passe ne peut pas contenir de séquences simples (123, abc, aaa)");
    }
    
    if (result.errors.length > 0) {
      result.isValid = false;
    }
    
    return result;
  }
  
  /**
   * Détecte les séquences faibles
   */
  private static hasWeakSequences(password: string): boolean {
    const passwordLower = password.toLowerCase();
    
    // Séquences numériques
    const weakNumeric = ['123', '234', '345', '456', '567', '678', '789', '890', 
                        '321', '432', '543', '654', '765', '876', '987', '098'];
    
    // Séquences alphabétiques
    const weakAlpha = ['abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 'hij', 
                      'ijk', 'jkl', 'klm', 'lmn', 'mno', 'nop', 'opq', 'pqr', 
                      'qrs', 'rst', 'stu', 'tuv', 'uvw', 'vwx', 'wxy', 'xyz',
                      'cba', 'dcb', 'edc', 'fed', 'gfe', 'hgf', 'ihg', 'jih'];
    
    // Répétitions (3 caractères identiques consécutifs)
    for (let i = 0; i < password.length - 2; i++) {
      if (password[i] === password[i + 1] && password[i] === password[i + 2]) {
        return true;
      }
    }
    
    // Vérification des séquences
    for (const seq of [...weakNumeric, ...weakAlpha]) {
      if (passwordLower.includes(seq)) {
        return true;
      }
    }
    
    return false;
  }
  
  /**
   * Calcule la force du mot de passe (0-100)
   */
  static calculateStrength(password: string): number {
    if (!password) return 0;
    
    let score = 0;
    
    // Longueur (0-25 points)
    if (password.length >= 8) score += 10;
    if (password.length >= 12) score += 10;
    if (password.length >= 16) score += 5;
    
    // Complexité (0-75 points)
    if (/[a-z]/.test(password)) score += 15;
    if (/[A-Z]/.test(password)) score += 15;
    if (/[0-9]/.test(password)) score += 15;
    if (/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(password)) score += 15;
    if (/[àáâãäåæçèéêëìíîïñòóôõöøùúûüýÿ]/.test(password.toLowerCase())) score += 5;
    if (password.length > 20) score += 10;
    
    // Pénalités
    if (this.hasWeakSequences(password)) score -= 20;
    if (password !== password.trim()) score -= 10;
    
    return Math.max(0, Math.min(100, score));
  }
}

/**
 * Validateur de champs génériques
 */
export class FieldValidator {
  /**
   * Valide un nom d'utilisateur
   */
  static validateUsername(username: string): ValidationResult {
    const result: ValidationResult = { isValid: true, errors: [] };
    
    if (!username) {
      result.errors.push("Le nom d'utilisateur est requis");
      result.isValid = false;
      return result;
    }
    
    const trimmed = username.trim();
    
    if (trimmed.length < 3) {
      result.errors.push("Le nom d'utilisateur doit contenir au moins 3 caractères");
    }
    if (trimmed.length > 50) {
      result.errors.push("Le nom d'utilisateur ne peut pas dépasser 50 caractères");
    }
    
    if (!/^[a-zA-Z][a-zA-Z0-9_-]*$/.test(trimmed)) {
      result.errors.push("Le nom d'utilisateur doit commencer par une lettre et ne contenir que des lettres, chiffres, tirets et underscores");
    }
    
    // Mots réservés
    const reservedWords = ['admin', 'administrator', 'root', 'user', 'test', 'api', 'www', 'ftp', 'mail', 'email', 'support'];
    if (reservedWords.includes(trimmed.toLowerCase())) {
      result.errors.push("Ce nom d'utilisateur est réservé");
    }
    
    if (result.errors.length > 0) {
      result.isValid = false;
    }
    
    return result;
  }
  
  /**
   * Valide un nom ou prénom
   */
  static validateName(name: string, fieldName: string = 'nom'): ValidationResult {
    const result: ValidationResult = { isValid: true, errors: [] };
    
    if (!name) {
      result.errors.push(`Le ${fieldName} est requis`);
      result.isValid = false;
      return result;
    }
    
    const trimmed = name.trim();
    
    if (trimmed.length < 2) {
      result.errors.push(`Le ${fieldName} doit contenir au moins 2 caractères`);
    }
    if (trimmed.length > 100) {
      result.errors.push(`Le ${fieldName} ne peut pas dépasser 100 caractères`);
    }
    
    // Pattern pour nom/prénom (lettres, espaces, tirets, apostrophes, caractères accentués)
    if (!/^[a-zA-ZÀ-ÿ][a-zA-ZÀ-ÿ\s\-']*[a-zA-ZÀ-ÿ]$/.test(trimmed) && trimmed.length > 1) {
      result.errors.push(`Le ${fieldName} ne peut contenir que des lettres, espaces, tirets et apostrophes`);
    } else if (trimmed.length === 1 && !/^[a-zA-ZÀ-ÿ]$/.test(trimmed)) {
      result.errors.push(`Le ${fieldName} ne peut contenir que des lettres`);
    }
    
    // Vérifier les espaces multiples
    if (/ {2}/.test(trimmed)) {
      result.errors.push(`Le ${fieldName} ne peut pas contenir d'espaces multiples`);
    }
    
    if (result.errors.length > 0) {
      result.isValid = false;
    }
    
    return result;
  }
  
  /**
   * Valide une adresse email
   */
  static validateEmail(email: string): ValidationResult {
    const result: ValidationResult = { isValid: true, errors: [] };
    
    if (!email) {
      result.errors.push("L'adresse email est requise");
      result.isValid = false;
      return result;
    }
    
    const trimmed = email.trim().toLowerCase();
    
    if (trimmed.length > 320) {
      result.errors.push("L'adresse email ne peut pas dépasser 320 caractères");
    }
    
    // Pattern email renforcé
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailPattern.test(trimmed)) {
      result.errors.push("Format d'adresse email invalide");
    }
    
    // Vérifications supplémentaires
    if (trimmed.includes('..')) {
      result.errors.push("L'adresse email ne peut pas contenir de points consécutifs");
    }
    
    if (trimmed.startsWith('.') || trimmed.startsWith('-')) {
      result.errors.push("L'adresse email ne peut pas commencer par un point ou un tiret");
    }
    
    // Domaines temporaires/jetables (liste partielle)
    const tempDomains = ['10minutemail.com', 'guerrillamail.com', 'tempmail.org', 'throwaway.email'];
    const domain = trimmed.split('@')[1];
    if (domain && tempDomains.includes(domain)) {
      result.errors.push("Les adresses email temporaires ne sont pas autorisées");
    }
    
    if (result.errors.length > 0) {
      result.isValid = false;
    }
    
    return result;
  }
}

/**
 * Validateur de formulaire complet
 */
export class FormValidator {
  /**
   * Valide toutes les données d'inscription
   */
  static validateRegistrationData(data: {
    username?: string;
    nom?: string;
    prenom?: string;
    email?: string;
    mot_de_passe?: string;
    confirmPassword?: string;
  }): FieldValidationResult {
    const results: FieldValidationResult = {};
    
    // Validation username
    results.username = FieldValidator.validateUsername(data.username || '');
    
    // Validation nom
    results.nom = FieldValidator.validateName(data.nom || '', 'nom');
    
    // Validation prénom
    results.prenom = FieldValidator.validateName(data.prenom || '', 'prénom');
    
    // Validation email
    results.email = FieldValidator.validateEmail(data.email || '');
    
    // Validation mot de passe
    results.mot_de_passe = PasswordValidator.validatePassword(data.mot_de_passe || '');
    
    // Validation confirmation mot de passe
    results.confirmPassword = { isValid: true, errors: [] };
    if (!data.confirmPassword) {
      results.confirmPassword.errors.push("La confirmation du mot de passe est requise");
      results.confirmPassword.isValid = false;
    } else if (data.mot_de_passe !== data.confirmPassword) {
      results.confirmPassword.errors.push("Les mots de passe ne correspondent pas");
      results.confirmPassword.isValid = false;
    }
    
    return results;
  }
  
  /**
   * Vérifie si toutes les validations sont réussies
   */
  static isFormValid(validationResults: FieldValidationResult): boolean {
    return Object.values(validationResults).every(result => result.isValid);
  }
  
  /**
   * Récupère toutes les erreurs de validation
   */
  static getAllErrors(validationResults: FieldValidationResult): string[] {
    const allErrors: string[] = [];
    
    Object.entries(validationResults).forEach(([field, result]) => {
      if (!result.isValid) {
        result.errors.forEach(error => {
          allErrors.push(`${field}: ${error}`);
        });
      }
    });
    
    return allErrors;
  }
}