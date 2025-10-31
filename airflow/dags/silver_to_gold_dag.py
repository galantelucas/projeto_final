from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import pandas as pd
import io
import os
from config.settings import make_s3_client, SILVER_BUCKET, GOLD_BUCKET


def list_silver_files():
    s3 = make_s3_client()
    response = s3.list_objects_v2(Bucket=SILVER_BUCKET)
    if "Contents" not in response:
        return []
    files = [obj["Key"] for obj in response["Contents"]]
    return files


def aggregate_to_gold():
    """Baixa todos os arquivos parquet do bucket silver, consolida e gera um arquivo no bucket gold.

    Estratégia genérica:
    - Concatena todos os Parquets encontrados
    - Se existir uma coluna datetime, agrega por período (ano-mês) somando colunas numéricas
    - Caso contrário, gera um arquivo de resumo (métricas básicas)
    """
    s3 = make_s3_client()

    files = list_silver_files()
    if not files:
        print("Nenhum arquivo encontrado no bucket silver. Nada a agregar.")
        return

    dfs = []
    for key in files:
        print(f"Baixando {key} do bucket silver")
        obj = s3.get_object(Bucket=SILVER_BUCKET, Key=key)
        data = obj["Body"].read()
        try:
            df = pd.read_parquet(io.BytesIO(data))
        except Exception:
            # tenta ler como CSV se parquet falhar
            try:
                df = pd.read_csv(io.StringIO(data.decode("utf-8")))
            except Exception as e:
                print(f"Falha ao ler {key}: {e}")
                continue
        dfs.append(df)

    if not dfs:
        print("Nenhum DataFrame válido encontrado para agregação.")
        return

    full = pd.concat(dfs, ignore_index=True)
    print(f"Total linhas concatenadas: {len(full)}")

    # Detecta colunas de data
    date_cols = [c for c in full.columns if 'date' in c.lower() or 'data' in c.lower()]

    if date_cols:
        # converter e agregar por ano-mês na primeira coluna de data
        dt_col = date_cols[0]
        try:
            full[dt_col] = pd.to_datetime(full[dt_col], errors='coerce')
            full['periodo'] = full[dt_col].dt.to_period('M').astype(str)
        except Exception:
            full['periodo'] = 'unknown'

        num_cols = full.select_dtypes(include='number').columns.tolist()
        if not num_cols:
            # se não há numéricas, apenas contar por periodo
            agg = full.groupby('periodo').size().reset_index(name='count')
        else:
            agg = full.groupby('periodo')[num_cols].sum().reset_index()

        # Serializar para parquet
        out_buffer = io.BytesIO()
        agg.to_parquet(out_buffer, index=False)
        out_key = f"aggregated_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.parquet"
        s3.put_object(Bucket=GOLD_BUCKET, Key=out_key, Body=out_buffer.getvalue())
        print(f"Agregado salvo em {GOLD_BUCKET}/{out_key}")
        return

    # Caso genérico: gerar resumo estatístico e enviar
    summary = {
        'rows': len(full),
        'cols': len(full.columns),
        'nulls_total': int(full.isnull().sum().sum()),
        'numeric_mean': full.select_dtypes(include='number').mean().to_dict()
    }

    # salvar summary como parquet (via DataFrame)
    summary_df = pd.DataFrame([summary])
    out_buffer = io.BytesIO()
    summary_df.to_parquet(out_buffer, index=False)
    out_key = f"summary_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.parquet"
    s3.put_object(Bucket=GOLD_BUCKET, Key=out_key, Body=out_buffer.getvalue())
    print(f"Resumo salvo em {GOLD_BUCKET}/{out_key}")


# ==============================
# 🪶 DEFINIÇÃO DA DAG
# ==============================
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "silver_to_gold_dag",
    default_args=default_args,
    description="Agrega arquivos Parquet do bucket silver e escreve resultados no bucket gold",
    schedule_interval="@daily",
    catchup=False,
) as dag:

    aggregate_task = PythonOperator(
        task_id="aggregate_silver_to_gold",
        python_callable=aggregate_to_gold,
    )

    aggregate_task
