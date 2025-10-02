from pydantic import BaseModel
from typing import Dict, Any, List, Optional

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

class HealthCheck(BaseModel):
    status: str
    timestamp: str