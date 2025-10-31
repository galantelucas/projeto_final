from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import pandas as pd
import io
import os
from config.settings import make_s3_client, BRONZE_BUCKET, SILVER_BUCKET

# A configuração do MinIO foi centralizada em `config/settings.py`.
# Use `make_s3_client()` para criar o cliente S3 e manter as credenciais
# fora dos arquivos de DAG.

# ==============================
# 🔧 FUNÇÕES
# ==============================

def list_bronze_files():
    """Lista todos os arquivos disponíveis no bucket bronze."""
    s3 = make_s3_client()
    response = s3.list_objects_v2(Bucket=BRONZE_BUCKET)
    if "Contents" not in response:
        return []
    files = [obj["Key"] for obj in response["Contents"]]
    return files


def convert_to_parquet():
    """Lê os arquivos do bronze, converte para Parquet e envia para o silver."""
    s3 = make_s3_client()

    files = list_bronze_files()
    if not files:
        print("Nenhum arquivo encontrado no bucket bronze.")
        return

    for file_name in files:
        print(f"Processando arquivo: {file_name}")

        # Baixar arquivo CSV para memória
        obj = s3.get_object(Bucket=BRONZE_BUCKET, Key=file_name)
        data = obj["Body"].read().decode("utf-8")
        df = pd.read_csv(io.StringIO(data))

        # Converter para parquet
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, index=False)

        # Gerar nome do novo arquivo
        parquet_name = os.path.splitext(file_name)[0] + ".parquet"

        # Fazer upload para o bucket silver
        s3.put_object(
            Bucket=SILVER_BUCKET,
            Key=parquet_name,
            Body=parquet_buffer.getvalue()
        )

        print(f"Arquivo convertido e salvo no bucket silver: {parquet_name}")


# ==============================
# 🪶 DEFINIÇÃO DA DAG
# ==============================
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    "bronze_to_silver_dag",
    default_args=default_args,
    description="Converte arquivos CSV do bucket bronze para parquet no bucket silver",
    schedule_interval=timedelta(minutes=5),
    catchup=False,
) as dag:

    transform_task = PythonOperator(
        task_id="convert_csv_to_parquet",
        python_callable=convert_to_parquet,
    )

    transform_task
