from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class CopilotQuery(BaseModel):
    dataset_id: str
    question: str


class CopilotResponse(BaseModel):
    answer: str
    supporting_data: Optional[Dict[str, Any]] = None


class ForecastRequest(BaseModel):
    dataset_id: str
    target_column: str
    date_column: str
    periods: int = 30
    model: str = "prophet"  # "prophet" or "xgboost"


class ForecastPoint(BaseModel):
    date: str
    predicted_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None


class ForecastResponse(BaseModel):
    target_column: str
    history_points: int
    forecast: List[ForecastPoint]


class SegmentSummary(BaseModel):
    segment: str
    customer_count: int
    avg_recency_days: float
    avg_frequency: float
    avg_monetary: float
    total_monetary: float


class SegmentationResponse(BaseModel):
    segments: Optional[List[SegmentSummary]] = None
    customers: Optional[List[Dict[str, Any]]] = None
    total_customers_analyzed: Optional[int] = None
    error: Optional[str] = None


class AnomalyResponse(BaseModel):
    total_rows_checked: Optional[int] = None
    anomalies_found: Optional[int] = None
    anomalies: Optional[List[Dict[str, Any]]] = None
    columns_analyzed: Optional[List[str]] = None
    error: Optional[str] = None
