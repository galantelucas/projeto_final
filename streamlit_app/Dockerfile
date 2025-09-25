# Imagem base Python slim
FROM python:3.10-slim

# Evitar interações durante instalação
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos de dependências primeiro para otimizar cache
COPY requirements.txt /app/

# Instala as dependências Python, incluindo versão clássica do GE
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir "great_expectations==0.13.48"

# Copia todo o projeto
COPY . /app

# Expondo porta padrão do Streamlit
EXPOSE 8501

# Comando de inicialização
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
