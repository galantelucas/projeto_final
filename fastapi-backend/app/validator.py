import pandas as pd
from typing import Dict, Any

class DataValidator:
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """Validação básica sem Great Expectations"""
        validation_results = {}
        for col in df.columns:
            # Validação simples: coluna não pode ter mais de 90% de nulos
            null_percentage = df[col].isnull().mean()
            validation_results[col] = null_percentage < 0.9
        
        num_cols = df.select_dtypes(include='number')
        
        return {
            "success": True,
            "rows": len(df),
            "cols": len(df.columns),
            "nulls_total": df.isnull().sum().sum(),
            "validation_results": validation_results,
            "basic_metrics": {
                "numeric_columns_mean": round(num_cols.mean().mean(), 2) if not num_cols.empty else 0,
                "nulls_by_column": df.isnull().sum().to_dict(),
                "data_types": df.dtypes.astype(str).to_dict()
            }
        }
    
    @staticmethod
    def detect_and_convert_dates(df: pd.DataFrame) -> pd.DataFrame:
        """Sua detecção automática de datas"""
        df_processed = df.copy()
        for col in df_processed.columns:
            if 'data' in col.lower() or 'date' in col.lower():
                try:
                    df_processed[col] = pd.to_datetime(df_processed[col], errors='coerce')
                except Exception:
                    pass
        return df_processed

# Instância global
validator = DataValidator()