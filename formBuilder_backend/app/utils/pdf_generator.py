"""Générateur de PDF"""

from weasyprint import HTML
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    @staticmethod
    def generate_from_html(
        html_content: str, output_path: Optional[str] = None
    ) -> bytes:
        """Générer un PDF à partir de HTML"""
        try:
            # Créer le document HTML
            html_doc = HTML(string=html_content)
            
            # Générer le PDF
            pdf_bytes = html_doc.write_pdf()
            
            if pdf_bytes is None:
                raise ValueError("Échec de la génération du PDF")
            
            # Sauvegarder si un chemin est fourni
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
            
            logger.info(f"PDF généré avec succès ({len(pdf_bytes)} bytes)")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du PDF: {str(e)}")
            raise ValueError(f"Erreur lors de la génération du PDF: {str(e)}")
