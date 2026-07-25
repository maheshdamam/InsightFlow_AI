from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud.dataset import get_dataset
from app.database import get_db
from app.models.user import User
from app.services.analytics import (
    breakdown_by,
    business_insights,
    compute_kpis,
    guess_column_mapping,
    revenue_trend,
)
from app.services.chart_data import (
    funnel_data,
    geo_data,
    heatmap_data,
    sankey_data,
    treemap_data,
)
from app.services.dataset_io import load_cleaned_dataset
from app.ai.recommendations import generate_recommendations
from app.utils.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _load_dataset_df(dataset_id: str, db: Session, current_user: User):
    dataset = get_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = load_cleaned_dataset(dataset.stored_path)
    mapping = guess_column_mapping(list(df.columns))
    return df, mapping


@router.get("/{dataset_id}/mapping")
def get_column_mapping(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Shows how columns were auto-mapped to business concepts (revenue, product, region, etc.)."""
    _, mapping = _load_dataset_df(dataset_id, db, current_user)
    return mapping


@router.get("/{dataset_id}/kpis")
def get_kpis(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df, mapping = _load_dataset_df(dataset_id, db, current_user)
    return compute_kpis(df, mapping)


@router.get("/{dataset_id}/trend")
def get_trend(
    dataset_id: str,
    freq: str = Query("M", description="D=daily, W=weekly, M=monthly, Q=quarterly, Y=yearly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    df, mapping = _load_dataset_df(dataset_id, db, current_user)
    return revenue_trend(df, mapping, freq=freq)


@router.get("/{dataset_id}/breakdown")
def get_breakdown(
    dataset_id: str,
    by: str = Query(..., description="One of: product, category, customer, region"),
    metric: str = Query("revenue", description="Metric to sum, e.g. revenue or profit"),
    top_n: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    df, mapping = _load_dataset_df(dataset_id, db, current_user)
    return breakdown_by(df, mapping, group_concept=by, metric_concept=metric, top_n=top_n)


@router.get("/{dataset_id}/insights")
def get_insights(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df, mapping = _load_dataset_df(dataset_id, db, current_user)
    return business_insights(df, mapping)


@router.get("/{dataset_id}/recommendations")
def get_recommendations(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df, _ = _load_dataset_df(dataset_id, db, current_user)
    return {"recommendations": generate_recommendations(df)}


@router.get("/{dataset_id}/heatmap")
def get_heatmap(
    dataset_id: str,
    row_by: str = Query("region", description="Concept to use as heatmap rows, e.g. region or product"),
    freq: str = Query("M", description="Time bucket for columns: D/W/M/Q/Y"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    df, mapping = _load_dataset_df(dataset_id, db, current_user)
    return heatmap_data(df, mapping, row_concept=row_by, freq=freq)


@router.get("/{dataset_id}/treemap")
def get_treemap(
    dataset_id: str,
    by: str = Query("product", description="Concept to group by, e.g. product or category"),
    top_n: int = 15,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    df, mapping = _load_dataset_df(dataset_id, db, current_user)
    return treemap_data(df, mapping, group_concept=by, top_n=top_n)


@router.get("/{dataset_id}/funnel")
def get_funnel(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df, mapping = _load_dataset_df(dataset_id, db, current_user)
    return funnel_data(df, mapping)


@router.get("/{dataset_id}/sankey")
def get_sankey(
    dataset_id: str,
    source: str = Query("category", description="Source node concept, e.g. category or product"),
    target: str = Query("region", description="Target node concept, e.g. region"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    df, mapping = _load_dataset_df(dataset_id, db, current_user)
    return sankey_data(df, mapping, source_concept=source, target_concept=target)


@router.get("/{dataset_id}/geo")
def get_geo(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df, mapping = _load_dataset_df(dataset_id, db, current_user)
    return geo_data(df, mapping)
