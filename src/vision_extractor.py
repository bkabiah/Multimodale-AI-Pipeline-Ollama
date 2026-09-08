import base64, io, json, logging, requests, uuid, re
from PIL import Image
from .schemas import EcommerceDocument, DocumentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionPlugin:
    def __init__(self, hf_token=None):
        self.ollama_url = "http://localhost:11434/api/chat"
        self.model_id = "moondream"

    def _encode_image(self, image):
        buffered = io.BytesIO()
        image.thumbnail((800, 800))
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def extract_data(self, image, doc_type):
        img_b64 = self._encode_image(image)
        prompt = 'Return ONLY valid JSON. Use EXACTLY these keys: "raw_text", "tables", "signatures", "entities". Do not use camelCase.'
        raw_content = "Unknown"
        try:
            payload = {
                "model": self.model_id,
                "messages": [{"role": "user", "content": prompt, "images": [img_b64]}],
                "stream": False,
                "format": "json",
                "options": {"repeat_penalty": 1.3, "num_predict": 400}
            }
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()
            
            raw_content = response.json()["message"]["content"]
            logger.info(f"RAW OUTPUT: {raw_content}")
            
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
            else:
                raise ValueError(f"Kein JSON gefunden.")
                
            return EcommerceDocument(document_id=str(uuid.uuid4()), document_type=doc_type, **parsed)
        except Exception as e:
            logger.error(f"Fehler: {e}")
            return EcommerceDocument(
                document_id=str(uuid.uuid4()), 
                document_type=doc_type, 
                raw_text=raw_content[:1000] if raw_content != "Unknown" else "Fehler", 
                entities={"error": str(e)}
            )