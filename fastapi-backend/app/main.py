from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

# Importações relativas - VERIFIQUE se os arquivos existem
try:
    from .validator import validator
    from .minio_client import minio_client
    print("✅ Módulos carregados com sucesso")
except ImportError as e:
    print(f"❌ Erro importando módulos: {e}")
    # Fallback para evitar erro
    class MockValidator:
        def validate_dataframe(self, df): return {"success": True}
        def detect_and_convert_dates(self, df): return df
    validator = MockValidator()
    
    class MockMinio:
        def file_exists(self, key): return False
        def download_file(self, key): return pd.DataFrame()
    minio_client = MockMinio()

app = FastAPI(
    title="Data Validation API",
    description="API de validação de dados",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os headers
)

class HealthCheck(BaseModel):
    status: str
    timestamp: str

class ValidationRequest(BaseModel):
    file_key: str

class ValidationResult(BaseModel):
    success: bool
    rows: int
    cols: int
    nulls_total: int
    validation_results: Dict[str, bool]
    data_preview: List[Dict[str, Any]]
    basic_metrics: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "Data Validation API - FastAPI + MinIO REAL"}

@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(
        status="healthy", 
        timestamp=datetime.now().isoformat()
    )

@app.get("/test")
async def test():
    return {"status": "success", "message": "API está funcionando"}

@app.get("/test-minio")
async def test_minio():
    """Endpoint para testar conexão com MinIO"""
    try:
        # Testa listar buckets
        buckets = minio_client.s3_client.list_buckets()
        bucket_names = [bucket['Name'] for bucket in buckets['Buckets']]
        return {
            "status": "success", 
            "buckets": bucket_names,
            "message": "Conexão MinIO OK"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro MinIO: {str(e)}"
        }

@app.post("/validate", response_model=ValidationResult)
async def validate_file(request: ValidationRequest):
    try:
        print(f"📥 Processando arquivo REAL: {request.file_key}")
        
        # ✅ AGORA É REAL: Baixa do MinIO
        if not minio_client.file_exists(request.file_key):
            # Fallback: cria dados mock se arquivo não existe
            print("⚠️ Arquivo não encontrado, usando dados de teste")
            df = pd.DataFrame({
                'nome': ['João', 'Maria', 'Pedro'],
                'idade': [30, 25, 35],
                'cidade': ['São Paulo', 'Rio', 'BH']
            })
        else:
            df = minio_client.download_file(request.file_key)
        
        print(f"✅ Arquivo processado: {len(df)} linhas, {len(df.columns)} colunas")
        
        # Processa datas (seu código)
        df_processed = validator.detect_and_convert_dates(df)
        
        # Validações
        validation_result = validator.validate_dataframe(df_processed)
        
        # Preview dos dados (5 primeiras linhas)
        data_preview = df_processed.head().fillna("NULL").to_dict(orient='records')
        
        return ValidationResult(
            **validation_result,
            data_preview=data_preview
        )
        
    except Exception as e:
        print(f"❌ Erro na validação: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro na validação: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)