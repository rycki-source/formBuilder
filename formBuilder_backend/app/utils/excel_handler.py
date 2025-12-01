"""Gestionnaire de fichiers Excel"""

import pandas as pd
from typing import List, Dict, Any
from io import BytesIO


class ExcelHandler:
    @staticmethod
    def read_excel(file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Lire un fichier Excel"""
        try:
            xl_file = pd.ExcelFile(file_path)
            data = {}
            for sheet_name in xl_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                data[sheet_name] = df.to_dict("records")
            return data
        except Exception as e:
            raise ValueError(f"Erreur lors de la lecture du fichier Excel: {str(e)}")

    @staticmethod
    def write_excel(data: List[Dict[str, Any]], output_path: str):
        """Écrire un fichier Excel"""
        try:
            df = pd.DataFrame(data)
            df.to_excel(output_path, index=False)
        except Exception as e:
            raise ValueError(f"Erreur lors de l'écriture du fichier Excel: {str(e)}")
