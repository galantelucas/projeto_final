import boto3
import pandas as pd
from io import BytesIO
import os
from botocore.exceptions import ClientError

class MinioClient:
    def __init__(self):
        self.endpoint_url = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minio")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minio123")
        self.bucket_name = "uploads"
        
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            verify=False
        )

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