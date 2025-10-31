import os
import streamlit as st
from botocore.exceptions import ClientError
from io import BytesIO
from config.settings import make_s3_client, BRONZE_BUCKET

class MinioClient:
    def __init__(self):
        # Cria cliente S3 centralizado e usa o bucket padrão definido em config
        self.s3_client = make_s3_client()
        self.bucket_name = os.getenv("MINIO_BUCKET", BRONZE_BUCKET)
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