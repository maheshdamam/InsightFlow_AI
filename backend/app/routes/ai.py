from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.copilot import ask_copilot
from app.crud.dataset import get_dataset
from app.database import get_db
from app.ml.forecasting import forecast_series
from app.ml.segmentation import segment_customers
from app.ml.anomaly import detect_anomalies
from app.models.user import User
from app.schemas.ai import (
    CopilotQuery,
    CopilotResponse,
    ForecastRequest,
    ForecastResponse,
    SegmentationResponse,
    AnomalyResponse,
)
from app.services.analytics import guess_column_mapping
from app.services.dataset_io import load_cleaned_dataset
from app.utils.deps import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Copilot & Forecasting"])


def _load_dataset_df(dataset_id: str, db: Session, current_user: User):
    dataset = get_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = load_cleaned_dataset(dataset.stored_path)
    return df


@router.post("/copilot", response_model=CopilotResponse)
def copilot_chat(payload: CopilotQuery, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = get_dataset(db, payload.dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_cleaned_dataset(dataset.stored_path)
    result = ask_copilot(df, payload.question, dataset_id=payload.dataset_id)
    return CopilotResponse(**result)


@router.post("/forecast", response_model=ForecastResponse)
def forecast(payload: ForecastRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = get_dataset(db, payload.dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_cleaned_dataset(dataset.stored_path)
    if payload.date_column not in df.columns or payload.target_column not in df.columns:
        raise HTTPException(status_code=400, detail="date_column or target_column not found in dataset")

    points = forecast_series(
        df, payload.date_column, payload.target_column, payload.periods, model=payload.model
    )
    return ForecastResponse(target_column=payload.target_column, history_points=len(df), forecast=points)


@router.get("/{dataset_id}/segments", response_model=SegmentationResponse)
def get_segments(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """K-Means customer segmentation (RFM: recency, frequency, monetary)."""
    df = _load_dataset_df(dataset_id, db, current_user)
    mapping = guess_column_mapping(list(df.columns))
    return segment_customers(df, mapping)


@router.get("/{dataset_id}/anomalies", response_model=AnomalyResponse)
def get_anomalies(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Isolation-Forest anomaly detection on revenue/profit/quantity columns."""
    df = _load_dataset_df(dataset_id, db, current_user)
    mapping = guess_column_mapping(list(df.columns))
    return detect_anomalies(df, mapping)
