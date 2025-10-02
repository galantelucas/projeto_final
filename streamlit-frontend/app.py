import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from great_expectations.dataset import PandasDataset
from io import BytesIO 

# ✅ PRIMEIRO COMANDO STREAMLIT - OBRIGATÓRIO
st.set_page_config(page_title="Data Validation Platform", layout="wide")

# ✅ IMPORTAÇÕES DEPOIS
try:
    from utils.minio_client import minio_client
    from utils.api_client import api_client
    MINIO_AVAILABLE = True
except ImportError as e:
    st.sidebar.warning(f"⚠️ Módulos de integração não disponíveis: {e}")
    MINIO_AVAILABLE = False

st.title("🚀 Streamlit-FastAPI-GE-MinIO-DataPlatform")

# Verificar saúde dos serviços
col1, col2 = st.columns(2)
with col1:
    try:
        # Tenta fazer uma requisição simples para a API
        import requests
        response = requests.get("http://fastapi-backend:8000/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ API Backend Online")
        else:
            st.error("❌ API Backend Com Problemas")
    except:
        st.error("❌ API Backend Offline")

with col2:
    try:
        import boto3
        # Tenta conectar ao MinIO
        s3_client = boto3.client(
            "s3",
            endpoint_url="http://minio:9000",
            aws_access_key_id="minio",
            aws_secret_access_key="minio123",
            verify=False
        )
        s3_client.list_buckets()
        st.success("✅ MinIO Storage Online")
    except:
        st.error("❌ MinIO Storage Offline")

# Modo de operação
operation_mode = st.radio(
    "Modo de Operação:",
    ["🚀 Usar Backend API (Recomendado)", "🔧 Processamento Local"],
    horizontal=True
)

uploaded_file = st.file_uploader("Faça upload do arquivo CSV", type=["csv"])

def display_validation_results(results, df):
    """Exibe resultados da validação da API"""
    
    st.subheader("✅ Resultados da Validação")
    
    # Métricas básicas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Linhas", results["rows"])
    col2.metric("Colunas", results["cols"])
    col3.metric("Valores Nulos", results["nulls_total"])
    col4.metric("Média Numérica", results["basic_metrics"]["numeric_columns_mean"])
    
    # Validações por coluna
    st.subheader("📊 Validações por Coluna")
    validation_df = pd.DataFrame.from_dict(
        results["validation_results"], 
        orient='index', 
        columns=["Validação Aprovada"]
    )
    st.dataframe(validation_df)
    
    # Nulos por coluna
    st.write("**🔍 Nulos por Coluna**")
    nulls_by_col = pd.DataFrame.from_dict(
        results["basic_metrics"]["nulls_by_column"],
        orient='index',
        columns=["Nulos"]
    )
    st.dataframe(nulls_by_col)
    
    # Preview dos dados
    st.subheader("👀 Prévia dos Dados")
    st.dataframe(df.head())
    
    # 📈 SEUS GRÁFICOS ATUAIS (mantidos)
    generate_visualizations(df)

def process_local_validation(df):
    """Seu código original de validação local"""
    # --- Detecta e converte automaticamente colunas de data ---
    for col in df.columns:
        if 'data' in col.lower() or 'date' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except Exception:
                pass

    st.subheader("Prévia dos dados")
    st.dataframe(df.head())

    # --- Métricas básicas ---
    st.subheader("Qualidade dos dados")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Linhas", len(df))
    col2.metric("Colunas", len(df.columns))
    col3.metric("Valores nulos (total)", df.isnull().sum().sum())
    num_cols = df.select_dtypes(include='number')
    col4.metric("Média valores numéricos", round(num_cols.mean().mean(), 2) if not num_cols.empty else 0)

    # Nulos por coluna
    st.write("**Linhas vazias por coluna**")
    st.write(df.isnull().sum())

    # --- Resumo estatístico ---
    st.subheader("Resumo estatístico")
    tab1, tab2 = st.tabs(["Numéricas", "Todas"])
    with tab1:
        st.write(df.describe())
    with tab2:
        st.write(df.describe(include='all').transpose())

    # --- Validação com Great Expectations ---
    st.subheader("Validação com Great Expectations")
    gdf = PandasDataset(df)

    # Regra: nenhuma coluna pode ser totalmente nula
    results = {}
    for col in df.columns:
        results[col] = gdf.expect_column_values_to_not_be_null(col)["success"]

    validation_df = pd.DataFrame.from_dict(results, orient='index', columns=["Coluna válida? Regra: nenhuma coluna pode ser totalmente nula"])
    st.write(validation_df)

    # Gera visualizações
    generate_visualizations(df)

def generate_visualizations(df):
    """Seu código original de visualizações"""
    st.subheader("Exploração visual")

    # --- Séries temporais ---
    date_cols = df.select_dtypes(include='datetime').columns
    if len(date_cols) > 0:
        for col in date_cols:
            st.write(f"📅 Série temporal baseada em {col}")
            agg_option = st.selectbox(
                f"Agrupar por (para {col}):",
                ["Mês", "Ano"],
                key=col
            )

            df_plot = df.copy()
            if agg_option == "Ano":
                df_plot["periodo"] = df_plot[col].dt.year.astype(str)
            else:
                df_plot["periodo"] = df_plot[col].dt.to_period("M").astype(str)

            num_cols = df.select_dtypes(include='number')
            if not num_cols.empty:
                num_col = num_cols.columns[0]
                df_grouped = df_plot.groupby("periodo")[num_col].sum().reset_index()

                fig, ax = plt.subplots(figsize=(4,3))
                ax.plot(df_grouped["periodo"], df_grouped[num_col], marker='o')
                ax.set_xlabel("Período")
                ax.set_ylabel(f"Total de {num_col}")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=False)

    # Colunas numéricas
    num_cols = df.select_dtypes(include='number')
    for col in num_cols.columns:
        st.write(f"📈 Distribuição: {col}")
        fig, ax = plt.subplots(1, 2, figsize=(4,3))
        sns.histplot(df[col].dropna(), kde=True, ax=ax[0])
        ax[0].set_title("Histograma")
        sns.boxplot(x=df[col].dropna(), ax=ax[1])
        ax[1].set_title("Boxplot")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)

    # Colunas categóricas
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in cat_cols:
        st.write(f"📊 Top categorias: {col}")
        fig, ax = plt.subplots(figsize=(4, 3))
        df[col].value_counts().head(10).plot(kind='bar', ax=ax)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)

    # Matriz de correlação para numéricas
    if len(num_cols.columns) > 1:
        st.subheader("Matriz de correlação")
        corr = num_cols.corr()
        fig, ax = plt.subplots(figsize=(4, 3))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues", ax=ax)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)

# FLUXO PRINCIPAL - VERSÃO CORRIGIDA
# FLUXO PRINCIPAL - VERSÃO CORRIGIDA (COM MANIPULAÇÃO CORRETA DO ARQUIVO)
if uploaded_file is not None:
    if operation_mode == "🚀 Usar Backend API (Recomendado)" and MINIO_AVAILABLE:
        with st.spinner("Enviando para validação..."):
            try:
                # 1. Testa API primeiro
                st.write("🔍 Verificando conexão com serviços...")
                
                if not api_client.health_check():
                    st.error("❌ API offline. Usando processamento local...")
                    uploaded_file.seek(0)  # Reset do arquivo
                    df = pd.read_csv(uploaded_file)
                    process_local_validation(df)
                
                else:
                    # 2. FAZ UPLOAD REAL PARA MINIO (COM CÓPIA SEGURA)
                    st.write("📤 Enviando arquivo para storage...")
                    
                    # Lê o conteúdo ANTES de fazer upload
                    uploaded_file.seek(0)
                    file_content = uploaded_file.read()
                    
                    # Faz upload da cópia
                    file_key = minio_client.upload_fileobj(file_content, uploaded_file.name)
                    st.success(f"✅ Arquivo '{file_key}' salvo no MinIO")
                    
                    # 3. CHAMA API PARA VALIDAÇÃO
                    st.write("🔍 Validando dados via API...")
                    results = api_client.validate_file(file_key)
                    
                    if results:
                        st.success("✅ Validação concluída via API!")
                        # Usa a cópia em memória para ler o CSV
                        df = pd.read_csv(BytesIO(file_content))
                        display_validation_results(results, df)
                    else:
                        st.error("❌ Falha na validação via API")
                        st.warning("🔄 Usando processamento local...")
                        df = pd.read_csv(BytesIO(file_content))
                        process_local_validation(df)
                    
            except Exception as e:
                st.error(f"🚨 Erro na integração: {str(e)}")
                st.warning("🔄 Usando processamento local...")
                # Tenta ler o arquivo original
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file)
                    process_local_validation(df)
                except:
                    st.error("❌ Não foi possível processar o arquivo")
    
    else:
        # 🔧 MODO LOCAL (seu código original) - SEMPRE FUNCIONA
        if operation_mode == "🚀 Usar Backend API (Recomendado)" and not MINIO_AVAILABLE:
            st.warning("🔧 Modo local - Integração MinIO/API não disponível")
        else:
            st.warning("🔧 Usando processamento local...")
        
        # Reset do arquivo antes de ler
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
        process_local_validation(df)

else:
    st.info("📤 Faça upload de um arquivo CSV para começar a validação.")