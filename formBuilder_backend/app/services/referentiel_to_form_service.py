"""
Service pour convertir des référentiels en formulaires
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.formulaire import Formulaire
from app.models.referentiel import Referentiel
from datetime import datetime


class ReferentielToFormConverter:
    """Convertit un référentiel en formulaire éditable"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _convert_referentiel_to_form_structure(self, referentiel_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convertit la structure d'un référentiel en structure de formulaire
        
        Args:
            referentiel_config: Configuration du référentiel (avec sections, groups, fields)
            
        Returns:
            Structure de formulaire compatible avec FormBuilder
        """
        form_structure = {
            "champs": [],
            "sections": []
        }
        
        sections = referentiel_config.get("sections", [])
        field_index = 0
        
        for section_idx, section in enumerate(sections):
            section_id = section.get("id", f"section_{section_idx}")
            section_title = section.get("title", f"Section {section_idx + 1}")
            
            # Ajouter la section
            form_structure["sections"].append({
                "id": section_id,
                "titre": section_title,
                "description": section.get("description", ""),
                "ordre": section_idx
            })
            
            # Parcourir les groupes de la section
            groups = section.get("groups", [])
            for group in groups:
                fields = group.get("fields", [])
                
                for field in fields:
                    # Convertir chaque champ du référentiel en champ de formulaire
                    form_field = self._convert_field(field, section_id, field_index)
                    if form_field:
                        form_structure["champs"].append(form_field)
                        field_index += 1
        
        return form_structure
    
    def _convert_field(self, ref_field: Dict[str, Any], section_id: str, index: int) -> Optional[Dict[str, Any]]:
        """
        Convertit un champ de référentiel en champ de formulaire
        
        Args:
            ref_field: Champ du référentiel
            section_id: ID de la section parente
            index: Index du champ
            
        Returns:
            Champ de formulaire ou None
        """
        field_id = ref_field.get("id", f"field_{index}")
        field_type = ref_field.get("type", "text")
        
        # Mapping des types de champs
        type_mapping = {
            "text": "text",
            "textarea": "textarea",
            "email": "email",
            "tel": "tel",
            "number": "number",
            "date": "date",
            "datetime-local": "datetime",
            "time": "time",
            "select": "select",
            "multiselect": "multiselect",
            "radio": "radio",
            "checkbox": "checkbox",
            "file": "file",
            "switch": "checkbox",
            "range": "range",
            "color": "color",
            "url": "url",
            "password": "password"
        }
        
        form_field = {
            "id": field_id,
            "nom": field_id,
            "label": ref_field.get("label", field_id),
            "type_champ": type_mapping.get(field_type, "text"),
            "section": section_id,
            "ordre": index,
            "obligatoire": ref_field.get("required", False),
            "placeholder": ref_field.get("placeholder", ""),
            "aide": ref_field.get("helpText", ""),
            "valeur_defaut": ref_field.get("defaultValue"),
        }
        
        # Ajouter les options pour les champs de sélection
        if field_type in ["select", "multiselect", "radio", "checkbox"]:
            options = ref_field.get("options", [])
            form_field["options"] = [
                {
                    "label": opt.get("label", opt.get("value", "")),
                    "valeur": opt.get("value", opt.get("label", ""))
                }
                for opt in options
            ]
        
        # Ajouter les validations
        validation = ref_field.get("validation", {})
        if validation:
            if "min" in validation:
                form_field["min"] = validation["min"]
            if "max" in validation:
                form_field["max"] = validation["max"]
            if "minLength" in validation:
                form_field["min_length"] = validation["minLength"]
            if "maxLength" in validation:
                form_field["max_length"] = validation["maxLength"]
            if "pattern" in validation:
                form_field["pattern"] = validation["pattern"]
        
        # Ajouter les conditions d'affichage
        if "showIf" in ref_field:
            form_field["condition"] = ref_field["showIf"]
        
        return form_field
    
    async def create_formulaire_from_referentiel(
        self,
        referentiel_id: int,
        user_id: int,
        auto_publish: bool = False
    ) -> Formulaire:
        """
        Crée un formulaire éditable à partir d'un référentiel
        
        Args:
            referentiel_id: ID du référentiel source
            user_id: ID de l'utilisateur créateur
            auto_publish: Publier automatiquement le formulaire
            
        Returns:
            Le formulaire créé
            
        Raises:
            ValueError: Si le référentiel n'existe pas ou est invalide
        """
        # Récupérer le référentiel
        from sqlalchemy import select
        result = await self.db.execute(
            select(Referentiel).where(Referentiel.id == referentiel_id)
        )
        referentiel = result.scalar_one_or_none()
        
        if not referentiel:
            raise ValueError(f"Référentiel {referentiel_id} introuvable")
        
        # Extraire la configuration
        metadata_json = referentiel.metadata_json or {}
        config = metadata_json.get("config", {})
        
        if not config:
            raise ValueError("Le référentiel ne contient pas de configuration")
        
        # Convertir en structure de formulaire
        form_structure = self._convert_referentiel_to_form_structure(config)
        
        if not form_structure["champs"]:
            raise ValueError("Le référentiel ne contient aucun champ")
        
        # Créer le formulaire
        formulaire = Formulaire(
            nom=metadata_json.get("name", referentiel.nom),
            description=metadata_json.get("description", referentiel.description),
            type_fonctionnel="referentiel",
            structure_json=form_structure,
            publie=auto_publish,
            version="1",
            developpeur_id=user_id,
            date_creation=datetime.utcnow(),
            date_modification=datetime.utcnow(),
            # Lien vers le référentiel source dans conditional_logic (sera utilisé pour metadata)
            conditional_logic={
                "referentiel_id": referentiel_id,
                "referentiel_version": referentiel.version,
                "source_type": referentiel.source_type,
                "imported_from": "referentiel",
                "import_date": datetime.utcnow().isoformat()
            }
        )
        
        self.db.add(formulaire)
        await self.db.commit()
        await self.db.refresh(formulaire)
        
        return formulaire
