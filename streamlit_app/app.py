import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from great_expectations.dataset import PandasDataset

st.set_page_config(page_title="Validação de CSV", layout="wide")

st.title("📊 Plataforma de Validação e Análise de Dados")

uploaded_file = st.file_uploader("Faça upload do arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # Carrega CSV com pandas
    df = pd.read_csv(uploaded_file)

    # --- Detecta e converte automaticamente colunas de data ---
    for col in df.columns:
        if 'data' in col.lower() or 'date' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except Exception:
                pass

    st.subheader("Prévia dos dados")
    st.dataframe(df.head())  # Top 5 linhas

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

    # --- Gráficos automáticos ---
    st.subheader("Exploração visual")

    # --- Séries temporais ---
    date_cols = df.select_dtypes(include='datetime').columns
    if len(date_cols) > 0:
        for col in date_cols:
            st.write(f"📅 Série temporal baseada em {col}")
            agg_option = st.selectbox(
                f"Agrupar por (para {col}):",
                ["Mês", "Ano"],  # apenas Mês ou Ano
                key=col  # chave para cada selectbox
            )

            df_plot = df.copy()
            if agg_option == "Ano":
                df_plot["periodo"] = df_plot[col].dt.year.astype(str)
            else:  # Mês
                df_plot["periodo"] = df_plot[col].dt.to_period("M").astype(str)

            if not num_cols.empty:
                num_col = num_cols.columns[0]

                # Soma
                df_grouped = df_plot.groupby("periodo")[num_col].sum().reset_index()

                fig, ax = plt.subplots(figsize=(4,3))
                ax.plot(df_grouped["periodo"], df_grouped[num_col], marker='o')
                ax.set_xlabel("Período")
                ax.set_ylabel(f"Total de {num_col}")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=False)

    # Colunas numéricas
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
        fig, ax =plt.subplots(figsize=(4, 3))
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

else:
    st.info("Faça upload de um arquivo CSV para começar.")
