from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from enum import Enum

class DocumentType(str, Enum):
    CONTRACT = "contract"
    INVOICE = "invoice"

class ExtractedSignature(BaseModel):
    is_present: bool
    signer_name: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)

class ExtractedTable(BaseModel):
    headers: List[str]
    rows: List[List[str]]

class EcommerceDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    document_id: str
    document_type: DocumentType
    raw_text: str = Field(alias="rawText", default="")
    tables: List[ExtractedTable] = []
    signatures: List[ExtractedSignature] = []
    entities: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)