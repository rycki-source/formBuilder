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

        for champ in structure.get("champs", []):
            champ_id = champ["id"]
            valeur = donnees.get(champ_id)

            # Vérifier si obligatoire
            if champ.get("obligatoire") and not valeur:
                if champ_id not in erreurs:
                    erreurs[champ_id] = []
                erreurs[champ_id].append("Ce champ est obligatoire")
                continue

            if valeur:
                # Valider le type
                type_champ = champ.get("type")
                error = ValidationService._validate_type(valeur, type_champ)
                if error:
                    if champ_id not in erreurs:
                        erreurs[champ_id] = []
                    erreurs[champ_id].append(error)

                # Appliquer les règles de validation
                for regle in champ.get("regles", []):
                    error = ValidationService._apply_rule(valeur, regle)
                    if error:
                        if champ_id not in erreurs:
                            erreurs[champ_id] = []
                        erreurs[champ_id].append(error)

        return len(erreurs) == 0, erreurs

    @staticmethod
    def _validate_type(valeur: Any, type_champ: str) -> Optional[str]:
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
