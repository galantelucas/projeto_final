# 📊 Streamlit-FastAPI-GE-MinIO-DataPlatform

## 🎯 **Visão Geral**
Plataforma moderna de validação e qualidade de dados com arquitetura microserviços, combinando análise automatizada com Great Expectations e storage cloud-native.

## 🏗️ **Arquitetura**

### **Stack Tecnológica**

Frontend: Streamlit (UI/UX)
Backend: FastAPI (Microserviço)
Validation: Great Expectations
Storage: MinIO (S3-compatible)
Orchestration: Docker Compose


### **Serviços**
| Serviço | Porta | Função |
|---------|-------|--------|
| `streamlit-frontend` | 8501 | Interface visual do usuário |
| `fastapi-backend` | 8000 | API de validação de dados |
| `minio` | 9000/9001 | Storage object (S3-like) |

## 🚀 **Funcionalidades**

### **Validação de Dados**
- ✅ **Análise automática** de schemas e tipos de dados
- ✅ **Detecção inteligente** de colunas de data
- ✅ **Validações com Great Expectations** (valores nulos, unicidade, etc.)
- ✅ **Métricas de qualidade** (completude, consistência)

### **Visualização & Análise**
- 📈 **Gráficos automáticos** (histogramas, boxplots, séries temporais)
- 📊 **Estatísticas descritivas** completas
- 🔍 **Matriz de correlação** para variáveis numéricas
- 📋 **Data profiling** automático

### **Storage & Escalabilidade**
- ☁️ **Storage cloud-native** com MinIO (S3 API)
- 🔄 **Processamento assíncrono** via API
- 📁 **Suporte a múltiplos formatos** (CSV, futuramente Parquet, JSON)
- 🏗️ **Arquitetura extensível** para novos conectores

## 🔄 **Fluxo de Dados**


Upload CSV → Streamlit UI

Storage → MinIO Bucket

Validação → FastAPI + Great Expectations

Resultados → Streamlit Dashboard

Fallback → Processamento local (se API offline)



## 🛠️ **Como Executar**

```bash
# Clone e execute
docker-compose up --build

# Acesse:
# Frontend: http://localhost:8501
# API Docs: http://localhost:8000/docs  
# MinIO Console: http://localhost:9001 (minio/minio123)