from fastapi import FastAPI, UploadFile, File, HTTPException
from .pipeline import ContractInteractionPipeline
from .schemas import DocumentType
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="E-Commerce Contract Pipeline API",
    description="Multimodale KI-Pipeline zur Extraktion von Verträgen und Rechnungen mit LLaMA 3.2 Vision.",
    version="1.0.0"
)

hf_token = os.getenv("HF_TOKEN")
pipeline = ContractInteractionPipeline(hf_token=hf_token or "dummy_token")

@app.post("/process/")
async def process_document(file: UploadFile = File(...), doc_type: DocumentType = DocumentType.CONTRACT):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Nur PDF-Dateien werden unterstützt.")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
        
    try:
        results = await pipeline.process_pdf(tmp_path, file.filename, doc_type)
        return {
            "status": "success",
            "filename": file.filename,
            "documents": [r.model_dump() for r in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ecommerce-contract-pipeline"}
