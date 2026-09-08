import boto3
import os
import logging
from botocore.exceptions import NoCredentialsError

logger = logging.getLogger(__name__)

class S3Plugin:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "eu-central-1")
        )
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "ecommerce-contracts-bucket")

    def upload_pdf(self, file_path: str, original_filename: str) -> str:
        """Lädt eine PDF in den S3 Bucket hoch und gibt den S3 Key zurück."""
        s3_key = f"raw_pdfs/{original_filename}"
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            logger.info(f"✅ PDF erfolgreich zu S3 hochgeladen: s3://{self.bucket_name}/{s3_key}")
            return f"s3://{self.bucket_name}/{s3_key}"
        except FileNotFoundError:
            logger.error("❌ Die Datei wurde nicht gefunden.")
            return ""
        except NoCredentialsError:
            logger.error("❌ AWS Credentials fehlen oder sind ungültig.")
            return ""
        except Exception as e:
            logger.error(f"❌ S3 Upload Fehler: {e}")
            return ""
