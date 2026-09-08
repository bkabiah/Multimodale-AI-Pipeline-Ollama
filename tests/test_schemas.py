import pytest
from src.schemas import EcommerceDocument, DocumentType, ExtractedSignature, ExtractedTable

def test_document_creation():
    doc = EcommerceDocument(
        document_id="123",
        document_type=DocumentType.CONTRACT,
        raw_text="Test Vertrag",
        signatures=[ExtractedSignature(is_present=True, signer_name="Max Mustermann", confidence=0.99)],
        tables=[ExtractedTable(headers=["Artikel", "Preis"], rows=[["Laptop", "1000"]])]
    )
    assert doc.document_type == DocumentType.CONTRACT
    assert doc.signatures[0].confidence == 0.99
    assert doc.tables[0].headers[0] == "Artikel"

def test_invalid_confidence():
    with pytest.raises(ValueError):
        # Confidence > 1.0 muss fehlschlagen (Pydantic Validation)
        ExtractedSignature(is_present=True, confidence=1.5)

