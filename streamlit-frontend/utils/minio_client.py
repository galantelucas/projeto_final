import boto3
import os
import streamlit as st
from botocore.exceptions import ClientError
from io import BytesIO

class MinioClient:
    def __init__(self):
        self.endpoint_url = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minio")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minio123")
        self.bucket_name = "bronze"

        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            verify=False
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Garante que o bucket existe"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            try:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            except Exception as e:
                st.error(f"❌ Erro criando bucket: {e}")

    def upload_fileobj(self, file_content, file_name: str) -> str:
        """Faz upload de arquivo para MinIO - aceita bytes ou file-like object"""
        try:
            # Se for bytes, converte para BytesIO
            if isinstance(file_content, bytes):
                file_obj = BytesIO(file_content)
            else:
                file_obj = file_content

            self.s3_client.upload_fileobj(
                Fileobj=file_obj,
                Bucket=self.bucket_name,
                Key=file_name
            )
            return file_name
        except Exception as e:
            st.error(f"❌ Erro no upload para MinIO: {str(e)}")
            raise

minio_client = MinioClient()