"""
Data-shaping functions for the newer chart types (heatmap, treemap, funnel,
sankey, geo). Kept separate from analytics.py since these return
chart-library-shaped structures rather than generic KPI/breakdown dicts.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd


def heatmap_data(
    df: pd.DataFrame,
    mapping: Dict[str, Optional[str]],
    row_concept: str = "region",
    freq: str = "M",
) -> Dict[str, Any]:
    """Grid of {row_label} x {time period} -> summed revenue, for a heatmap."""
    row_col, date_col, revenue_col = mapping.get(row_concept), mapping.get("date"), mapping.get("revenue")
    if not row_col or not date_col or not revenue_col:
        return {"rows": [], "columns": [], "cells": []}
    if row_col not in df.columns or date_col not in df.columns or revenue_col not in df.columns:
        return {"rows": [], "columns": [], "cells": []}

    from app.services.analytics import FREQ_ALIASES

    work = df[[row_col, date_col, revenue_col]].copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work = work.dropna(subset=[date_col])
    # to_period() wants the plain letter (D/W/M/Q/Y), unlike resample() which
    # needs the newer ME/QE/YE aliases — so we deliberately don't use FREQ_ALIASES here.
    period_freq = freq.upper() if freq.upper() in ("D", "W", "M", "Q", "Y") else "M"
    work["period"] = work[date_col].dt.to_period(period_freq).astype(str)

    pivot = work.pivot_table(index=row_col, columns="period", values=revenue_col, aggfunc="sum", fill_value=0)
    # Keep the grid to a manageable size for rendering
    if len(pivot) > 12:
        pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).head(12).index]
    if len(pivot.columns) > 12:
        pivot = pivot[sorted(pivot.columns)[-12:]]

    rows = [str(r) for r in pivot.index]
    columns = [str(c) for c in pivot.columns]
    cells = [
        {"row": str(r), "column": str(c), "value": float(pivot.loc[r, c])}
        for r in pivot.index
        for c in pivot.columns
    ]
    return {"rows": rows, "columns": columns, "cells": cells}


def treemap_data(
    df: pd.DataFrame,
    mapping: Dict[str, Optional[str]],
    group_concept: str = "product",
    top_n: int = 15,
) -> List[Dict[str, Any]]:
    """[{name, value}] shaped for Recharts' <Treemap>."""
    group_col, revenue_col = mapping.get(group_concept), mapping.get("revenue")
    if not group_col or group_col not in df.columns:
        return []
    if revenue_col and revenue_col in df.columns:
        grouped = df.groupby(group_col)[revenue_col].sum().sort_values(ascending=False).head(top_n)
        return [{"name": str(idx), "value": round(float(val), 2)} for idx, val in grouped.items() if val > 0]
    counts = df[group_col].value_counts().head(top_n)
    return [{"name": str(idx), "value": int(val)} for idx, val in counts.items()]


def funnel_data(df: pd.DataFrame, mapping: Dict[str, Optional[str]]) -> List[Dict[str, Any]]:
    """
    Generic sales datasets rarely have explicit pipeline stages, so this
    builds a meaningful funnel directly from the numbers you do have:
    all orders -> profitable orders -> above-median revenue -> top decile revenue.
    If a genuine 'stage' style column exists it's used directly instead.
    """
    revenue_col, profit_col = mapping.get("revenue"), mapping.get("profit")

    stage_col = None
    for col in df.columns:
        if col.lower() in ("stage", "funnel_stage", "status", "pipeline_stage"):
            stage_col = col
            break

    if stage_col:
        counts = df[stage_col].value_counts()
        return [{"stage": str(idx), "value": int(val)} for idx, val in counts.items()]

    if not revenue_col or revenue_col not in df.columns:
        return []

    total = len(df)
    stages = [{"stage": "All Orders", "value": total}]

    if profit_col and profit_col in df.columns:
        profitable = int((df[profit_col] > 0).sum())
        stages.append({"stage": "Profitable Orders", "value": profitable})

    median_rev = df[revenue_col].median()
    above_median = int((df[revenue_col] > median_rev).sum())
    stages.append({"stage": "Above-Median Revenue", "value": above_median})

    top_decile_cutoff = df[revenue_col].quantile(0.9)
    top_decile = int((df[revenue_col] >= top_decile_cutoff).sum())
    stages.append({"stage": "Top 10% Orders", "value": top_decile})

    return stages


def sankey_data(
    df: pd.DataFrame,
    mapping: Dict[str, Optional[str]],
    source_concept: str = "category",
    target_concept: str = "region",
    top_n: int = 8,
) -> Dict[str, Any]:
    """{nodes: [{name}], links: [{source, target, value}]} shaped for a D3 sankey."""
    source_col = mapping.get(source_concept) or mapping.get("product")
    target_col = mapping.get(target_concept)
    revenue_col = mapping.get("revenue")

    if not source_col or not target_col or source_col not in df.columns or target_col not in df.columns:
        return {"nodes": [], "links": []}

    work = df[[source_col, target_col] + ([revenue_col] if revenue_col in df.columns else [])].copy()

    if revenue_col and revenue_col in df.columns:
        grouped = work.groupby([source_col, target_col])[revenue_col].sum().reset_index()
        grouped = grouped.rename(columns={revenue_col: "value"})
    else:
        grouped = work.groupby([source_col, target_col]).size().reset_index(name="value")

    # Keep it readable: top N source categories by total flow
    top_sources = grouped.groupby(source_col)["value"].sum().sort_values(ascending=False).head(top_n).index
    grouped = grouped[grouped[source_col].isin(top_sources)]

    sources = [f"{s} (source)" for s in grouped[source_col].unique()]
    targets = [f"{t} (dest)" for t in grouped[target_col].unique()]
    node_names = sources + targets
    node_index = {name: i for i, name in enumerate(node_names)}

    links = [
        {
            "source": node_index[f"{row[source_col]} (source)"],
            "target": node_index[f"{row[target_col]} (dest)"],
            "value": round(float(row["value"]), 2),
        }
        for _, row in grouped.iterrows()
        if row["value"] > 0
    ]

    nodes = [{"name": n.replace(" (source)", "").replace(" (dest)", "")} for n in node_names]
    return {"nodes": nodes, "links": links}


def geo_data(df: pd.DataFrame, mapping: Dict[str, Optional[str]]) -> List[Dict[str, Any]]:
    """[{region, value}] — region names are matched client-side against a world atlas."""
    region_col, revenue_col = mapping.get("region"), mapping.get("revenue")
    if not region_col or region_col not in df.columns:
        return []
    if revenue_col and revenue_col in df.columns:
        grouped = df.groupby(region_col)[revenue_col].sum().sort_values(ascending=False)
        return [{"region": str(idx), "value": round(float(val), 2)} for idx, val in grouped.items()]
    counts = df[region_col].value_counts()
    return [{"region": str(idx), "value": int(val)} for idx, val in counts.items()]
