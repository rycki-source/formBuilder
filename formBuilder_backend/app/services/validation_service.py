from typing import Dict, Any, List, Tuple, Optional
import re


class ValidationService:
    """Moteur de validation pour les soumissions de formulaire"""

    @staticmethod
    def validate_soumission(
        donnees: Dict[str, Any], structure: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, List[str]]]:
        """Valider une soumission contre la structure du formulaire"""
        erreurs = {}

        # Gestion de structure vide ou invalide
        if not structure or not isinstance(structure, dict):
            return True, {}  # Pas de validation si pas de structure
            
        champs = structure.get("champs", [])
        if not champs:
            return True, {}  # Pas de champs à valider

        for champ in champs:
            # Identifier le champ de manière flexible
            champ_id = champ.get("id")
            champ_label = champ.get("label")
            champ_nom = champ.get("nom")
            
            # Chercher la valeur avec différents identifiants possibles
            valeur = None
            identifiant_trouve = None
            
            for identifiant in [champ_id, champ_label, champ_nom]:
                if identifiant and identifiant in donnees:
                    valeur = donnees[identifiant]
                    identifiant_trouve = identifiant
                    break
            
            # Si aucun identifiant trouvé, utiliser le premier disponible pour les erreurs
            if not identifiant_trouve:
                identifiant_trouve = champ_id or champ_label or champ_nom or "champ_inconnu"

            # Vérifier si obligatoire
            if champ.get("obligatoire") and not valeur:
                if identifiant_trouve not in erreurs:
                    erreurs[identifiant_trouve] = []
                erreurs[identifiant_trouve].append("Ce champ est obligatoire")
                continue

            if valeur:
                # Valider le type
                type_champ = champ.get("type_champ") or champ.get("type")
                error = ValidationService._validate_type(valeur, type_champ)
                if error:
                    if identifiant_trouve not in erreurs:
                        erreurs[identifiant_trouve] = []
                    erreurs[identifiant_trouve].append(error)

                # Appliquer les règles de validation
                for regle in champ.get("regles", []):
                    error = ValidationService._apply_rule(valeur, regle)
                    if error:
                        if identifiant_trouve not in erreurs:
                            erreurs[identifiant_trouve] = []
                        erreurs[identifiant_trouve].append(error)

        return len(erreurs) == 0, erreurs

    @staticmethod
    def _validate_type(valeur: Any, type_champ: str) -> Optional[str]:
        """Valider le type d'une valeur"""
        if not type_champ or not valeur:
            return None
            
        # Convertir la valeur en string pour la validation si nécessaire
        valeur_str = str(valeur).strip() if valeur is not None else ""
        
        if type_champ in ["email", "e-mail"]:
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(pattern, valeur_str):
                return "Format d'email invalide"
        
        elif type_champ in ["number", "nombre", "numeric"]:
            try:
                float(valeur_str)
            except (ValueError, TypeError):
                return "Doit être un nombre valide"
        
        elif type_champ == "tel":
            # Pattern basique pour les numéros de téléphone
            pattern = r"^[+]?[\d\s\-\.\(\)]{8,15}$"
            if not re.match(pattern, valeur_str):
                return "Format de téléphone invalide"
        
        elif type_champ == "url":
            pattern = r"^https?://[\w\.-]+\.[a-zA-Z]{2,}/?.*$"
            if not re.match(pattern, valeur_str):
                return "Format d'URL invalide"
        
        return None
        """Valider le type d'un champ"""
        if type_champ == "email":
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", valeur):
                return "Email invalide"
        elif type_champ == "number":
            try:
                float(valeur)
            except ValueError:
                return "Doit être un nombre"
        elif type_champ == "date":
            try:
                from datetime import datetime

                datetime.fromisoformat(valeur)
            except ValueError:
                return "Format de date invalide"
        elif type_champ == "geolocation":
            # Valider structure géolocalisation: {latitude, longitude, accuracy?}
            if not isinstance(valeur, dict):
                return "Format de géolocalisation invalide"
            if "latitude" not in valeur or "longitude" not in valeur:
                return "Latitude et longitude requises"
            try:
                lat = float(valeur["latitude"])
                lng = float(valeur["longitude"])
                if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                    return "Coordonnées GPS invalides"
            except (ValueError, TypeError):
                return "Coordonnées GPS invalides"
        elif type_champ == "signature":
            # Valider que la signature est une chaîne base64
            if not isinstance(valeur, str):
                return "Format de signature invalide"
            if not valeur.startswith("data:image/"):
                return "La signature doit être une image"
        return None

    @staticmethod
    def _apply_rule(valeur: str, regle: Dict[str, Any]) -> Optional[str]:
        """Appliquer une règle de validation"""
        rule_type = regle.get("type")

        if rule_type == "regex":
            pattern = regle.get("expression")
            if pattern and not re.match(pattern, str(valeur)):
                return regle.get("message_erreur", "Validation échouée")

        elif rule_type == "min":
            min_val = regle.get("expression")
            if min_val is not None and len(str(valeur)) < int(min_val):
                return regle.get("message_erreur", f"Minimum {min_val} caractères")

        elif rule_type == "max":
            max_val = regle.get("expression")
            if max_val is not None and len(str(valeur)) > int(max_val):
                return regle.get("message_erreur", f"Maximum {max_val} caractères")

        return None
