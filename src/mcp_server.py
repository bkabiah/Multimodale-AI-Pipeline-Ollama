from mcp.server import Server
import logging
import psycopg2
import os
import json
from .schemas import EcommerceDocument

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Server("ecommerce-db-mcp")

def get_db_connection():
    """Holt die Verbindung zur Cloud-Datenbank."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432")
    )

@app.tool()
async def save_document_to_db(doc_json: str) -> str:
    """Speichert ein validiertes E-Commerce Dokument in der PostgreSQL Cloud-Datenbank."""
    try:
        doc = EcommerceDocument.model_validate_json(doc_json)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Tabelle erstellen, falls sie nicht existiert (nur für den ersten Start nützlich)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id VARCHAR(255) PRIMARY KEY,
                type VARCHAR(50),
                data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Daten einfügen (oder updaten)
        cur.execute("""
            INSERT INTO documents (id, type, data)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data;
        """, (doc.document_id, doc.document_type.value, doc.model_dump_json()))
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"✅ Dokument {doc.document_id} in Cloud-DB gespeichert.")
        return f"Dokument {doc.document_id} erfolgreich in der Cloud-Datenbank gespeichert."
    except Exception as e:
        logger.error(f"❌ DB Fehler: {str(e)}")
        return f"Fehler beim Speichern: {str(e)}"

@app.tool()
async def query_contract_status(contract_id: str) -> str:
    """Fragt den Status eines Vertrags in der Datenbank ab."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT type, created_at FROM documents WHERE id = %s;", (contract_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            return f"Vertrag {contract_id} ist vom Typ '{result[0]}' und wurde am {result[1]} archiviert."
        return f"Vertrag {contract_id} wurde nicht gefunden."
    except Exception as e:
        return f"Fehler bei der Abfrage: {str(e)}"
