# 📊 Data Platform — Documentação Técnica

Autores:
- Wilkerson Carvalho - 2417568
- Lucas Galante - 2417572

## 🎯 Visão geral

Este repositório contém uma plataforma de ingestão, validação e orquestração de dados construída com Streamlit (UI), FastAPI (API), MinIO (object storage), Great Expectations (validação) e Apache Airflow (orquestração). O projeto segue o padrão medallion (bronze → silver → gold) e foi organizado para execução via Docker Compose.

O objetivo desta documentação é fornecer instruções técnicas para instalar, configurar, executar e estender a plataforma em um ambiente local/containerizado.

---

## 🏗️ Arquitetura e componentes

Diagrama de arquitetura: `docs/architecture.svg`

### Stack tecnológica
- Frontend: Streamlit
- Backend: FastAPI
- Validação: Great Expectations
- Storage: MinIO (S3-compatible)
- Orquestração: Apache Airflow (DAGs em `airflow/dags`)
- Banco de dados do Airflow: Postgres (via Docker Compose)

### Serviços principais (resumo)
| Serviço | Porta | Observação |
|--------:|:-----:|:----------|
| `streamlit-frontend` | 8501 | Interface para upload/visualização de dados |
| `fastapi-backend` | 8000 | Endpoints de validação e testes (/health, /test-minio, /validate) |
| `minio` | 9000 (API) / 9001 (Console) | Object storage; buckets: `bronze`, `silver`, `gold` |
| `create_buckets` | — | Serviço de inicialização que cria buckets no MinIO (usado no compose)
| `postgres` | 5432 | Backend do Airflow |
| `airflow-webserver` | 8080 | UI do Airflow; DAGs disponíveis em `airflow/dags` |

---

## Estrutura do repositório (resumida)

- `airflow/` — Dockerfile, requisitos e DAGs (`airflow/dags/bronze_to_silver_dag.py`, `airflow/dags/silver_to_gold_dag.py`)
- `fastapi-backend/app/` — aplicação FastAPI (`main.py`, `minio_client.py`, `validator.py`, `schemas.py`)
- `streamlit-frontend/` — app Streamlit (`app.py`) e utilitários
- `config/` — módulo central de configurações (variáveis de ambiente, helper `make_s3_client()`)
- `great_expectations/` — guia e (futuras) expectativas
- `storage/minio_data/` — dados usados localmente pelo MinIO (ex.: `bronze/vendas_exemplo.csv`)
- `docker-compose.yml` — orquestração dos containers

---

## ⚙️ Requisitos

- Docker (>= 20.x) e Docker Compose
- (Opcional) Python 3.9+ para executar serviços localmente sem Docker

Recomendado: ter 4GB de RAM livre para executar todos os serviços locais.

---

## � Quickstart — execução via Docker Compose

1. Copie o arquivo de exemplo de variáveis de ambiente e ajuste os valores:

```bash
cp .env.example .env
# Edite .env conforme necessário (especialmente MINIO_* e nomes de buckets)
```

2. Suba a stack (build + start):

```bash
docker-compose up --build -d
```

3. Verifique status e acesse as UIs:

- Streamlit: http://localhost:8501
- FastAPI (docs): http://localhost:8000/docs
- MinIO Console: http://localhost:9001
- Airflow Webserver: http://localhost:8080

4. Logs e troubleshooting:

```bash
docker-compose logs -f streamlit-frontend
docker-compose logs -f fastapi-backend
docker-compose logs -f minio
docker-compose logs -f airflow-webserver
```

Observações importantes:
- O projeto já contém `.env.example` com variáveis necessárias. Nunca comite `.env` com credenciais reais (há `.gitignore` para isso).
- `docker-compose.yml` monta o diretório do projeto dentro dos containers em `/opt/project` e define `PYTHONPATH=/opt/project` para permitir importações de `config`.

---

## 🔐 Configuração e variáveis de ambiente

As variáveis principais (definidas em `.env` ou ambiente do container):

- MINIO_ENDPOINT — endpoint MinIO (ex.: `minio:9000`)
- MINIO_ACCESS_KEY — access key do MinIO
- MINIO_SECRET_KEY — secret key do MinIO
- BRONZE_BUCKET — nome do bucket bronze (ex.: `bronze`)
- SILVER_BUCKET — nome do bucket silver (ex.: `silver`)
- GOLD_BUCKET — nome do bucket gold (ex.: `gold`)
- API_URL — URL base da API FastAPI (usada pelo frontend)
- STREAMLIT_SERVER_MAXUPLOADSIZE — (opcional) limite de upload do Streamlit

Veja `./.env.example` para valores padrões usados em desenvolvimento.

---

## ▶️ Como os DAGs funcionam (Airflow)

- Os DAGs estão em `airflow/dags` e são detectados automaticamente pelo Airflow se o serviço for iniciado com o volume que aponta para esse diretório.
- Principais DAGs:
  - `bronze_to_silver_dag.py`: converte CSVs do bucket `bronze` para Parquet no `silver`.
  - `silver_to_gold_dag.py`: agrega os Parquets do `silver` e escreve os resultados no `gold` (resumo/aggregação por período).

Como acionar manualmente (via UI): vá para o Airflow Webserver em `http://localhost:8080`, selecione o DAG e clique em `Trigger DAG`.


---

## 🧪 Endpoints úteis (FastAPI)

- GET `/` — rota raiz
- GET `/health` — verifica saúde do serviço
- GET `/test` — teste simples
- GET `/test-minio` — verifica conexão com MinIO
- POST `/validate` — endpoint para validação (veja `fastapi-backend/app/schemas.py` e `validator.py`)

Exemplo rápido (curl):

```bash
curl -s http://localhost:8000/health
```

---

## 🧭 Desenvolvimento local (alternativa ao Docker)

Se preferir rodar componentes localmente sem Docker:

1. Crie e ative um virtualenv com Python 3.9+.
2. Instale dependências nos `requirements.txt` (cada serviço tem o seu):

```bash
pip install -r fastapi-backend/requirements.txt
pip install -r streamlit-frontend/requirements.txt
pip install -r airflow/requirements.txt
```

3. Exporte variáveis de ambiente conforme `.env.example` e execute os serviços (ex.: `uvicorn fastapi-backend.app.main:app --reload --host 0.0.0.0 --port 8000`, `streamlit run streamlit-frontend/app.py`).

Observação: ao rodar localmente, garanta que o MinIO esteja acessível e que `config/settings.py` encontre as variáveis de ambiente.

---

## 🧰 Troubleshooting comum

- ImportError/Dependências: se faltar pacotes dentro de um container, verifique os `requirements.txt` e reconstrua a imagem (`docker-compose build --no-cache`).
- Erros de import `config`: o compose monta o projeto em `/opt/project` e define `PYTHONPATH=/opt/project`; se alterar, ajuste o `PYTHONPATH` ou copie `config/` para o pacote Python do container.
- MinIO: verifique credenciais em `.env`; para console, acesse `http://localhost:9001`.
- Airflow: se DAGs não aparecerem, confirme se o volume do DAGs está montado corretamente e verifique os logs do `airflow-webserver`.

