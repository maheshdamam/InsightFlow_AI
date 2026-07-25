"""
Anomaly detection for revenue/profit rows using Isolation Forest.

Isolation Forest is used (rather than a simple z-score) because it handles
multivariate anomalies well — e.g. a row with normal revenue but a wildly
disproportionate profit margin gets flagged even if neither column alone
looks extreme.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(
    df: pd.DataFrame,
    mapping: Dict[str, Optional[str]],
    contamination: float = 0.05,
) -> Dict[str, Any]:
    numeric_cols = [
        mapping.get(c) for c in ("revenue", "profit", "quantity")
        if mapping.get(c) and mapping.get(c) in df.columns
    ]
    if not numeric_cols:
        return {"error": "No numeric business columns (revenue/profit/quantity) detected to check for anomalies."}

    work = df[numeric_cols].dropna()
    if len(work) < 10:
        return {"error": "Not enough rows to reliably detect anomalies (need at least 10)."}

    model = IsolationForest(contamination=contamination, random_state=42, n_estimators=200)
    predictions = model.fit_predict(work)  # -1 = anomaly, 1 = normal
    scores = model.decision_function(work)  # lower = more anomalous

    work = work.copy()
    work["is_anomaly"] = predictions == -1
    work["anomaly_score"] = scores

    date_col, product_col = mapping.get("date"), mapping.get("product")
    extra_cols = [c for c in (date_col, product_col) if c and c in df.columns]
    result_df = df.loc[work.index, extra_cols].copy() if extra_cols else pd.DataFrame(index=work.index)
    for col in numeric_cols:
        result_df[col] = work[col]
    result_df["anomaly_score"] = work["anomaly_score"].round(4)
    result_df["is_anomaly"] = work["is_anomaly"]

    anomalies = result_df[result_df["is_anomaly"]].sort_values("anomaly_score").drop(columns=["is_anomaly"])

    return {
        "total_rows_checked": int(len(work)),
        "anomalies_found": int(len(anomalies)),
        "anomalies": anomalies.head(50).to_dict(orient="records"),
        "columns_analyzed": numeric_cols,
    }
