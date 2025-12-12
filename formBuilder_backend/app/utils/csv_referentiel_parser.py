"""
Utilitaire pour parser les fichiers CSV de référentiels de formulaires
Structure attendue du CSV:

Section,Field ID,Field Label,Field Type,Required,Options,Validation Rules,Conditions
Section 1,field_1,Nom,text,true,,min:2;max:50,
Section 1,field_2,Email,email,true,,pattern:^[^@]+@[^@]+$,
Section 2,field_3,Pays,select,true,"France;Belgique;Suisse",,
"""

import csv
from typing import Dict, Any, List
from io import StringIO


class CSVReferentielParser:
    """Parser pour les référentiels CSV"""
    
    @staticmethod
    def parse_csv_file(file_path: str) -> Dict[str, Any]:
        """
        Parser un fichier CSV de référentiel
        
        Args:
            file_path: Chemin vers le fichier CSV
            
        Returns:
            Dict contenant la configuration du formulaire
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return CSVReferentielParser.parse_csv_content(content)
    
    @staticmethod
    def parse_csv_content(content: str) -> Dict[str, Any]:
        """
        Parser le contenu CSV d'un référentiel
        
        Args:
            content: Contenu CSV sous forme de string
            
        Returns:
            Dict contenant la configuration du formulaire
        """
        csv_reader = csv.DictReader(StringIO(content))
        
        # Regrouper par sections
        sections_dict: Dict[str, Dict[str, Any]] = {}
        
        for row in csv_reader:
            section_name = row.get('Section', 'Section par défaut').strip()
            
            if section_name not in sections_dict:
                sections_dict[section_name] = {
                    'id': section_name.lower().replace(' ', '_'),
                    'title': section_name,
                    'groups': [{
                        'id': f"{section_name.lower().replace(' ', '_')}_group",
                        'fields': []
                    }]
                }
            
            # Parser le champ
            field = {
                'id': row.get('Field ID', '').strip(),
                'label': row.get('Field Label', '').strip(),
                'type': row.get('Field Type', 'text').strip().lower(),
                'required': row.get('Required', 'false').strip().lower() == 'true',
            }
            
            # Options (pour select, radio, etc.)
            options_str = row.get('Options', '').strip()
            if options_str:
                field['options'] = [opt.strip() for opt in options_str.split(';')]
            
            # Validation rules
            validation_str = row.get('Validation Rules', '').strip()
            if validation_str:
                validation = {}
                for rule in validation_str.split(';'):
                    if ':' in rule:
                        key, value = rule.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Convertir les valeurs numériques
                        if key in ['min', 'max', 'minLength', 'maxLength']:
                            try:
                                validation[key] = int(value)
                            except ValueError:
                                validation[key] = value
                        else:
                            validation[key] = value
                
                if validation:
                    field['validation'] = validation
            
            # Conditions
            conditions_str = row.get('Conditions', '').strip()
            if conditions_str:
                conditions = []
                for cond in conditions_str.split(';'):
                    if ':' in cond:
                        parts = cond.split(':')
                        if len(parts) == 3:
                            conditions.append({
                                'field': parts[0].strip(),
                                'operator': parts[1].strip(),
                                'value': parts[2].strip()
                            })
                if conditions:
                    field['conditions'] = conditions
            
            # Ajouter le champ à sa section
            sections_dict[section_name]['groups'][0]['fields'].append(field)
        
        # Convertir en liste
        sections = list(sections_dict.values())
        
        return {
            'config': {
                'id': 'form',
                'version': '1.0.0',
                'name': 'Formulaire importé depuis CSV',
                'sections': sections
            }
        }
    
    @staticmethod
    def create_csv_template(output_path: str):
        """
        Créer un template CSV vide
        
        Args:
            output_path: Chemin où sauvegarder le template
        """
        headers = [
            'Section',
            'Field ID',
            'Field Label',
            'Field Type',
            'Required',
            'Options',
            'Validation Rules',
            'Conditions'
        ]
        
        example_rows = [
            {
                'Section': 'Informations personnelles',
                'Field ID': 'nom',
                'Field Label': 'Nom',
                'Field Type': 'text',
                'Required': 'true',
                'Options': '',
                'Validation Rules': 'min:2;max:50',
                'Conditions': ''
            },
            {
                'Section': 'Informations personnelles',
                'Field ID': 'email',
                'Field Label': 'Email',
                'Field Type': 'email',
                'Required': 'true',
                'Options': '',
                'Validation Rules': 'pattern:^[^@]+@[^@]+$',
                'Conditions': ''
            },
            {
                'Section': 'Informations personnelles',
                'Field ID': 'pays',
                'Field Label': 'Pays',
                'Field Type': 'select',
                'Required': 'true',
                'Options': 'France;Belgique;Suisse;Canada',
                'Validation Rules': '',
                'Conditions': ''
            },
            {
                'Section': 'Coordonnées',
                'Field ID': 'telephone',
                'Field Label': 'Téléphone',
                'Field Type': 'tel',
                'Required': 'false',
                'Options': '',
                'Validation Rules': 'pattern:^\\+?[0-9]{10,15}$',
                'Conditions': ''
            },
            {
                'Section': 'Informations avancées',
                'Field ID': 'localisation',
                'Field Label': 'Ma position',
                'Field Type': 'geolocation',
                'Required': 'false',
                'Options': '',
                'Validation Rules': '',
                'Conditions': ''
            },
            {
                'Section': 'Informations avancées',
                'Field ID': 'signature',
                'Field Label': 'Signature',
                'Field Type': 'signature',
                'Required': 'true',
                'Options': '',
                'Validation Rules': '',
                'Conditions': ''
            }
        ]
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(example_rows)


if __name__ == "__main__":
    # Créer un template
    CSVReferentielParser.create_csv_template("template_referentiel.csv")
    print("✅ Template CSV créé: template_referentiel.csv")
    
    # Tester le parser
    result = CSVReferentielParser.parse_csv_file("template_referentiel.csv")
    print(f"✅ Parser testé: {len(result['config']['sections'])} sections")
    for section in result['config']['sections']:
        fields_count = len(section['groups'][0]['fields'])
        print(f"  - {section['title']}: {fields_count} champs")
