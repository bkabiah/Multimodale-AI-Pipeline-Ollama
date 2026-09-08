from pdf2image import convert_from_path
from .vision_extractor import VisionPlugin
from .s3_plugin import S3Plugin
from .schemas import DocumentType
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractInteractionPipeline:
    def __init__(self, hf_token: str):
        self.vision_plugin = VisionPlugin(hf_token)
        self.s3_plugin = S3Plugin()

    async def process_pdf(self, pdf_path: str, original_filename: str, doc_type: DocumentType):
        logger.info(f"Starte Verarbeitung für: {original_filename}")
        
        # 1. PDF zu S3 hochladen (Backup)
        s3_uri = self.s3_plugin.upload_pdf(pdf_path, original_filename)
        
        # 2. PDF in Bilder konvertieren
        images = convert_from_path(pdf_path, dpi=150)
        
        results = []
        for i, image in enumerate(images):
            logger.info(f"Verarbeite Seite {i+1} von {len(images)}...")
            doc_data = self.vision_plugin.extract_data(image, doc_type)
            
            # S3 URI in den Metadaten speichern
            doc_data.metadata["s3_uri"] = s3_uri
            doc_data.metadata["original_filename"] = original_filename
            results.append(doc_data)
            
        logger.info(f"✅ Verarbeitung abgeschlossen. {len(results)} Dokumente extrahiert.")
        return results
