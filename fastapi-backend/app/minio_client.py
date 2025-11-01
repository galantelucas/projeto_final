import pandas as pd
from io import BytesIO
import os
from botocore.exceptions import ClientError
from config.settings import make_s3_client, BRONZE_BUCKET

class MinioClient:
    def __init__(self):
        # Usa cliente S3 centralizado a partir de `config.settings`
        self.s3_client = make_s3_client()
        self.bucket_name = os.getenv("MINIO_BUCKET", BRONZE_BUCKET)

    def download_file(self, file_key: str) -> pd.DataFrame:
        """Baixa arquivo do MinIO e retorna DataFrame"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            # Lê o CSV diretamente do stream
            df = pd.read_csv(BytesIO(response["Body"].read()))
            return df
        except ClientError as e:
            raise Exception(f"Erro ao baixar arquivo {file_key}: {str(e)}")

    def file_exists(self, file_key: str) -> bool:
        """Verifica se arquivo existe no MinIO"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except ClientError:
            return False

# Instância global
minio_client = MinioClient()