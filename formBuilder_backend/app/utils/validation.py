"""
Utilitaires de validation centralisés pour l'application
Règles de validation strictes pour tous les champs
"""

import re
from typing import List, Optional, Dict, Any
from pydantic import ValidationError


class ValidationResult:
    """Résultat d'une validation avec détails"""
    def __init__(self, is_valid: bool = True, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: str):
        """Ajouter une erreur"""
        self.is_valid = False
        self.errors.append(error)


class PasswordValidator:
    """Validateur de mot de passe avec règles strictes"""
    
    @staticmethod
    def validate_password(password: str) -> ValidationResult:
        """
        Valide un mot de passe selon les règles strictes :
        - Longueur : 8-128 caractères
        - Au moins 1 majuscule
        - Au moins 1 minuscule  
        - Au moins 1 chiffre
        - Au moins 1 caractère spécial (!@#$%^&*()_+-=[]{}|;:,.<>?)
        - Pas d'espaces en début/fin
        - Pas de séquences simples (123, abc, aaa)
        """
        result = ValidationResult()
        
        if not password:
            result.add_error("Le mot de passe est requis")
            return result
        
        # Longueur
        if len(password) < 8:
            result.add_error("Le mot de passe doit contenir au moins 8 caractères")
        if len(password) > 128:
            result.add_error("Le mot de passe ne peut pas dépasser 128 caractères")
        
        # Espaces en début/fin
        if password != password.strip():
            result.add_error("Le mot de passe ne peut pas commencer ou finir par un espace")
        
        # Majuscules
        if not re.search(r'[A-Z]', password):
            result.add_error("Le mot de passe doit contenir au moins une majuscule")
        
        # Minuscules
        if not re.search(r'[a-z]', password):
            result.add_error("Le mot de passe doit contenir au moins une minuscule")
        
        # Chiffres
        if not re.search(r'[0-9]', password):
            result.add_error("Le mot de passe doit contenir au moins un chiffre")
        
        # Caractères spéciaux
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            result.add_error("Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*()_+-=[]{}|;:,.<>?)")
        
        # Séquences faibles
        if PasswordValidator._has_weak_sequences(password):
            result.add_error("Le mot de passe ne peut pas contenir de séquences simples (123, abc, aaa)")
        
        return result
    
    @staticmethod
    def _has_weak_sequences(password: str) -> bool:
        """Détecte les séquences faibles dans le mot de passe"""
        password_lower = password.lower()
        
        # Séquences numériques
        weak_numeric = ['123', '234', '345', '456', '567', '678', '789', '890', '321', '432', '543', '654', '765', '876', '987', '098']
        
        # Séquences alphabétiques
        weak_alpha = ['abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 'hij', 'ijk', 'jkl', 'klm', 'lmn', 'mno', 'nop', 'opq', 'pqr', 'qrs', 'rst', 'stu', 'tuv', 'uvw', 'vwx', 'wxy', 'xyz']
        weak_alpha += [seq[::-1] for seq in weak_alpha]  # Séquences inversées
        
        # Répétitions
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        
        # Vérification des séquences
        for seq in weak_numeric + weak_alpha:
            if seq in password_lower:
                return True
        
        return False


class FieldValidator:
    """Validateur pour les autres champs du formulaire"""
    
    @staticmethod
    def validate_username(username: str) -> ValidationResult:
        """
        Valide un nom d'utilisateur :
        - 3-50 caractères
        - Lettres, chiffres, tirets, underscores uniquement
        - Commence par une lettre
        - Pas de caractères spéciaux
        """
        result = ValidationResult()
        
        if not username:
            result.add_error("Le nom d'utilisateur est requis")
            return result
        
        username = username.strip()
        
        if len(username) < 3:
            result.add_error("Le nom d'utilisateur doit contenir au moins 3 caractères")
        if len(username) > 50:
            result.add_error("Le nom d'utilisateur ne peut pas dépasser 50 caractères")
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
            result.add_error("Le nom d'utilisateur doit commencer par une lettre et ne contenir que des lettres, chiffres, tirets et underscores")
        
        # Mots réservés
        reserved_words = ['admin', 'administrator', 'root', 'user', 'test', 'api', 'www', 'ftp', 'mail', 'email', 'support']
        if username.lower() in reserved_words:
            result.add_error("Ce nom d'utilisateur est réservé")
        
        return result
    
    @staticmethod
    def validate_name(name: str, field_name: str = "nom") -> ValidationResult:
        """
        Valide un nom ou prénom :
        - 2-100 caractères
        - Lettres, espaces, tirets, apostrophes uniquement
        - Commence et finit par une lettre
        """
        result = ValidationResult()
        
        if not name:
            result.add_error(f"Le {field_name} est requis")
            return result
        
        name = name.strip()
        
        if len(name) < 2:
            result.add_error(f"Le {field_name} doit contenir au moins 2 caractères")
        if len(name) > 100:
            result.add_error(f"Le {field_name} ne peut pas dépasser 100 caractères")
        
        if not re.match(r"^[a-zA-ZÀ-ÿ][a-zA-ZÀ-ÿ\s\-']*[a-zA-ZÀ-ÿ]$", name) and len(name) > 1:
            result.add_error(f"Le {field_name} ne peut contenir que des lettres, espaces, tirets et apostrophes")
        elif len(name) == 1 and not re.match(r"^[a-zA-ZÀ-ÿ]$", name):
            result.add_error(f"Le {field_name} ne peut contenir que des lettres")
        
        # Vérifier les espaces multiples
        if '  ' in name:
            result.add_error(f"Le {field_name} ne peut pas contenir d'espaces multiples")
        
        return result
    
    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """
        Valide une adresse email :
        - Format email standard
        - Longueur maximale 320 caractères
        - Domaine valide
        """
        result = ValidationResult()
        
        if not email:
            result.add_error("L'adresse email est requise")
            return result
        
        email = email.strip().lower()
        
        if len(email) > 320:
            result.add_error("L'adresse email ne peut pas dépasser 320 caractères")
        
        # Pattern email renforcé
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            result.add_error("Format d'adresse email invalide")
        
        # Vérifications supplémentaires
        if '..' in email:
            result.add_error("L'adresse email ne peut pas contenir de points consécutifs")
        
        if email.startswith('.') or email.startswith('-'):
            result.add_error("L'adresse email ne peut pas commencer par un point ou un tiret")
        
        # Domaines temporaires/jetables (liste partielle)
        temp_domains = ['10minutemail.com', 'guerrillamail.com', 'tempmail.org', 'throwaway.email']
        domain = email.split('@')[1] if '@' in email else ''
        if domain in temp_domains:
            result.add_error("Les adresses email temporaires ne sont pas autorisées")
        
        return result


class FormValidator:
    """Validateur complet pour les formulaires"""
    
    @staticmethod
    def validate_registration_data(data: Dict[str, Any]) -> ValidationResult:
        """Valide toutes les données d'inscription"""
        result = ValidationResult()
        
        # Validation username
        username_result = FieldValidator.validate_username(data.get('username', ''))
        if not username_result.is_valid:
            result.errors.extend([f"Nom d'utilisateur: {error}" for error in username_result.errors])
            result.is_valid = False
        
        # Validation nom
        nom_result = FieldValidator.validate_name(data.get('nom', ''), 'nom')
        if not nom_result.is_valid:
            result.errors.extend(nom_result.errors)
            result.is_valid = False
        
        # Validation prénom
        prenom_result = FieldValidator.validate_name(data.get('prenom', ''), 'prénom')
        if not prenom_result.is_valid:
            result.errors.extend(prenom_result.errors)
            result.is_valid = False
        
        # Validation email
        email_result = FieldValidator.validate_email(data.get('email', ''))
        if not email_result.is_valid:
            result.errors.extend(email_result.errors)
            result.is_valid = False
        
        # Validation mot de passe
        password_result = PasswordValidator.validate_password(data.get('mot_de_passe', ''))
        if not password_result.is_valid:
            result.errors.extend(password_result.errors)
            result.is_valid = False
        
        return result


# Fonctions d'aide pour l'utilisation avec Pydantic
def validate_password_strength(password: str) -> str:
    """Fonction de validation pour Pydantic"""
    result = PasswordValidator.validate_password(password)
    if not result.is_valid:
        raise ValueError("; ".join(result.errors))
    return password


def validate_username_format(username: str) -> str:
    """Fonction de validation pour Pydantic"""
    result = FieldValidator.validate_username(username)
    if not result.is_valid:
        raise ValueError("; ".join(result.errors))
    return username


def validate_name_format(name: str) -> str:
    """Fonction de validation pour Pydantic"""
    result = FieldValidator.validate_name(name)
    if not result.is_valid:
        raise ValueError("; ".join(result.errors))
    return name