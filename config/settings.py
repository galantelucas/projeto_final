import os
from typing import Any


# Arquivo central de configurações para o projeto.
# As variáveis sensíveis são carregadas a partir de variáveis de ambiente.
# Para desenvolvimento, copie `.env.example` para `.env` e não o inclua no Git.

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
# As credenciais devem ser definidas no .env (não usar valores sensíveis no código).
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

# Nomes padrão dos buckets
BRONZE_BUCKET = os.getenv("BRONZE_BUCKET", "bronze")
SILVER_BUCKET = os.getenv("SILVER_BUCKET", "silver")
GOLD_BUCKET = os.getenv("GOLD_BUCKET", "gold")


def make_s3_client() -> Any:
    """Cria um cliente S3 (boto3) usando as variáveis de ambiente.

    Use esta função nas DAGs e scripts em vez de instanciar clients diretamente,
    para centralizar a configuração.
    """
    import boto3

    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )
