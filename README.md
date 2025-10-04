# 📊 Streamlit-FastAPI-GE-MinIO-DataPlatform

Alunos:
Wilkerson Carvalho -
Lucas Galante - 2417572


## 🎯 **Visão Geral**
Plataforma moderna de validação e qualidade de dados com arquitetura de microserviços, combinando análise automatizada com Great Expectations, storage cloud-native e orquestração com Airflow.

---

## 🏗️ **Arquitetura**

### **Stack Tecnológica**
- **Frontend:** Streamlit (UI/UX)
- **Backend:** FastAPI (Microserviço)
- **Validation:** Great Expectations
- **Storage:** MinIO (S3-compatible)
- **Orchestration:** Airflow + Docker Compose
- **Database:** Postgres (Airflow backend)

---

### **Serviços**
| Serviço | Porta | Função |
|---------|-------|--------|
| `streamlit-frontend` | 8501 | Interface visual do usuário |
| `fastapi-backend` | 8000 | API de validação de dados |
| `minio` | 9000/9001 | Storage object (S3-like) |
| `create_buckets` | - | Cria buckets `bronze`, `silver` e `gold` no MinIO |
| `postgres` | 5432 | Banco de dados Airflow |
| `airflow-init` | - | Inicializa DB Airflow e cria usuário admin |
| `airflow-webserver` | 8080 | Interface web do Airflow |
| `airflow-scheduler` | - | Executa DAGs do Airflow |

---

## 🚀 **Funcionalidades**

### **Validação de Dados**
- ✅ Análise automática de schemas e tipos de dados
- ✅ Detecção inteligente de colunas de data
- ✅ Validações com Great Expectations (valores nulos, unicidade, etc.)
- ✅ Métricas de qualidade (completude, consistência)

### **Visualização & Análise**
- 📈 Gráficos automáticos (histogramas, boxplots, séries temporais)
- 📊 Estatísticas descritivas completas
- 🔍 Matriz de correlação para variáveis numéricas
- 📋 Data profiling automático

### **Storage & Escalabilidade**
- ☁️ Storage cloud-native com MinIO (S3 API)
- 🔄 Processamento assíncrono via API
- 📁 Suporte a múltiplos formatos (CSV, futuramente Parquet, JSON)
- 🏗️ Arquitetura extensível para novos conectores

### **Orquestração e Workflow**
- 🛠️ Airflow com LocalExecutor e Postgres como backend
- ⏱️ Inicialização automática do DB e criação do usuário admin (`admin/admin`)
- 📦 DAGs podem processar arquivos de MinIO automaticamente
- ✅ Wait-for-it integrado para garantir que Postgres e MinIO estejam prontos antes de iniciar Airflow

---

## 🔄 **Fluxo de Dados**

1. **Upload CSV** → Streamlit UI
2. **Storage** → MinIO Bucket (`bronze`)
3. **Orquestração** → Airflow DAGs processam e movem dados de `bronze → silver → gold`
4. **Validação** → FastAPI + Great Expectations
5. **Resultados** → Streamlit Dashboard
6. **Fallback** → Processamento local se API offline

---

## 🛠️ **Como Executar**

```bash
# Clone o repositório
git clone <repo_url>
cd <repo>

# Suba todos os serviços
docker-compose up --build
```

### **Acessos**
- **Frontend Streamlit:** http://localhost:8501
- **API FastAPI:** http://localhost:8000/docs
- **MinIO Console:** http://localhost:9001
  - Usuário: `minio`
  - Senha: `minio123`
- **Airflow Webserver:** http://localhost:8080
  - Usuário: `admin`
  - Senha: `admin`

---

## ⚡ **Observações Técnicas**
- Airflow usa **LocalExecutor + Postgres** para execução paralela segura
- O init do Airflow aguarda o Postgres estar pronto antes de inicializar o DB e criar o usuário
- MinIO é inicializado com os buckets `bronze`, `silver` e `gold` públicos
- DAGs podem ser adicionadas em `./airflow/dags` e são montadas via volume

