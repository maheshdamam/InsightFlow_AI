"""
Customer segmentation using K-Means clustering on RFM features:
- Recency: days since the customer's most recent order
- Frequency: number of orders
- Monetary: total revenue from that customer

Falls back to whatever numeric columns are available if a customer or date
column isn't mapped, so this still produces *something* useful on datasets
without a clean customer identifier.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

SEGMENT_LABELS = ["At Risk", "Occasional", "Loyal", "Champions"]


def _label_segments(centers: np.ndarray) -> Dict[int, str]:
    """
    Rank cluster centers by an overall 'value' score (higher frequency +
    monetary, lower recency = better) and assign human-readable labels so the
    dashboard doesn't just show 'Cluster 2'.
    """
    # centers columns are [recency, frequency, monetary] in scaled space
    score = -centers[:, 0] + centers[:, 1] + centers[:, 2]
    order = np.argsort(score)  # worst -> best
    labels = {}
    n = len(order)
    label_pool = SEGMENT_LABELS if n <= 4 else [f"Segment {i+1}" for i in range(n)]
    for rank, cluster_idx in enumerate(order):
        labels[int(cluster_idx)] = label_pool[min(rank, len(label_pool) - 1)]
    return labels


def segment_customers(
    df: pd.DataFrame,
    mapping: Dict[str, Optional[str]],
    n_clusters: int = 4,
) -> Dict[str, Any]:
    customer_col = mapping.get("customer")
    revenue_col = mapping.get("revenue")
    date_col = mapping.get("date")

    if not customer_col or customer_col not in df.columns:
        return {"error": "No customer column detected — segmentation needs a customer identifier."}
    if not revenue_col or revenue_col not in df.columns:
        return {"error": "No revenue column detected — segmentation needs a monetary value."}

    work = df.copy()
    if date_col and date_col in work.columns:
        work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
        reference_date = work[date_col].max()
    else:
        reference_date = None

    grouped = work.groupby(customer_col).agg(
        frequency=(revenue_col, "count"),
        monetary=(revenue_col, "sum"),
    )

    if reference_date is not None:
        last_purchase = work.groupby(customer_col)[date_col].max()
        grouped["recency"] = (reference_date - last_purchase).dt.days.fillna(grouped["frequency"].max())
    else:
        # No usable date column: treat every customer as equally recent so
        # clustering still runs on frequency + monetary alone.
        grouped["recency"] = 0

    grouped = grouped.dropna()
    if len(grouped) < n_clusters:
        return {"error": f"Not enough distinct customers ({len(grouped)}) to form {n_clusters} segments."}

    features = grouped[["recency", "frequency", "monetary"]].values
    scaled = StandardScaler().fit_transform(features)

    k = min(n_clusters, len(grouped))
    model = KMeans(n_clusters=k, n_init=10, random_state=42)
    cluster_ids = model.fit_predict(scaled)
    grouped["cluster"] = cluster_ids

    labels_by_cluster = _label_segments(model.cluster_centers_)
    grouped["segment"] = grouped["cluster"].map(labels_by_cluster)

    summary: List[Dict[str, Any]] = []
    for cluster_id, segment_name in labels_by_cluster.items():
        subset = grouped[grouped["cluster"] == cluster_id]
        summary.append({
            "segment": segment_name,
            "customer_count": int(len(subset)),
            "avg_recency_days": round(float(subset["recency"].mean()), 1),
            "avg_frequency": round(float(subset["frequency"].mean()), 1),
            "avg_monetary": round(float(subset["monetary"].mean()), 2),
            "total_monetary": round(float(subset["monetary"].sum()), 2),
        })

    summary.sort(key=lambda s: s["total_monetary"], reverse=True)

    top_customers = (
        grouped.reset_index()
        .sort_values("monetary", ascending=False)
        .head(15)[[customer_col, "segment", "recency", "frequency", "monetary"]]
        .rename(columns={customer_col: "customer"})
        .to_dict(orient="records")
    )

    return {
        "segments": summary,
        "customers": top_customers,
        "total_customers_analyzed": int(len(grouped)),
    }
