"""
Business analytics engine.

Datasets can have arbitrary column names, so this module first heuristically
maps common business concepts (revenue, profit, date, product, customer,
region) to whichever columns best match, then computes KPIs, trends, and
breakdowns on top of that mapping. Users can override the mapping later via
the /analytics/mapping endpoint if the heuristics guess wrong.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

COLUMN_HINTS = {
    "revenue": ["revenue", "sales", "amount", "total", "price"],
    "profit": ["profit", "margin", "net_income"],
    "date": ["date", "order_date", "created_at", "timestamp"],
    "product": [
    "product_name",
    "product name",
    "name",
    "item_name",
    "item",
    "product",
    "sku",
    "product_id",
    "productid",
    ],
    "category": ["category", "product_category", "segment"],
    "customer": ["customer", "client", "buyer"],
    "region": ["region", "state", "country", "city"],
    "quantity": ["quantity", "qty", "units"],
}


def guess_column_mapping(columns: List[str]) -> Dict[str, Optional[str]]:
    mapping = {}

    normalized = {c.lower().replace(" ", "_"): c for c in columns}

    for concept, hints in COLUMN_HINTS.items():
        mapping[concept] = None

        for hint in hints:
            for norm, original in normalized.items():
                if norm == hint:
                    mapping[concept] = original
                    break
            if mapping[concept]:
                break

        if mapping[concept] is None:
            for hint in hints:
                for norm, original in normalized.items():
                    if hint in norm:
                        mapping[concept] = original
                        break
                if mapping[concept]:
                    break

    return mapping


def compute_kpis(df: pd.DataFrame, mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
    kpis: Dict[str, Any] = {}

    revenue_col = mapping.get("revenue")
    profit_col = mapping.get("profit")
    customer_col = mapping.get("customer")
    quantity_col = mapping.get("quantity")
    if revenue_col and revenue_col in df.columns:
        kpis["total_revenue"] = float(df[revenue_col].sum())
        kpis["average_order_value"] = float(df[revenue_col].mean())
    if profit_col and profit_col in df.columns:
        kpis["total_profit"] = float(df[profit_col].sum())
        if revenue_col and revenue_col in df.columns and df[revenue_col].sum() != 0:
            kpis["profit_margin_pct"] = round(
                float(df[profit_col].sum() / df[revenue_col].sum() * 100), 2
            )
    if customer_col and customer_col in df.columns:
        kpis["total_customers"] = int(df[customer_col].nunique())
    if quantity_col and quantity_col in df.columns:
        kpis["total_units_sold"] = float(df[quantity_col].sum())

    kpis["total_orders"] = int(len(df))
    return kpis


# Accept friendly, human-typed frequency letters and map them to the
# pandas 2.2+ offset aliases (e.g. "M" for month-end was renamed to "ME").
FREQ_ALIASES = {"D": "D", "W": "W", "M": "ME", "Q": "QE", "Y": "YE"}


def revenue_trend(df: pd.DataFrame, mapping: Dict[str, Optional[str]], freq: str = "M") -> List[Dict[str, Any]]:
    date_col, revenue_col = mapping.get("date"), mapping.get("revenue")
    if not date_col or not revenue_col or date_col not in df.columns or revenue_col not in df.columns:
        return []
    tmp = df[[date_col, revenue_col]].copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp = tmp.dropna(subset=[date_col])
    resolved_freq = FREQ_ALIASES.get(freq.upper(), freq)
    grouped = tmp.set_index(date_col).resample(resolved_freq)[revenue_col].sum().reset_index()
    return [
        {"period": row[date_col].strftime("%Y-%m-%d"), "revenue": float(row[revenue_col])}
        for _, row in grouped.iterrows()
    ]


def breakdown_by(df: pd.DataFrame, mapping: Dict[str, Optional[str]], group_concept: str, metric_concept: str = "revenue", top_n: int = 10) -> List[Dict[str, Any]]:
    group_col, metric_col = mapping.get(group_concept), mapping.get(metric_concept)
    if not group_col or group_col not in df.columns:
        return []
    if metric_col and metric_col in df.columns:
        grouped = df.groupby(group_col)[metric_col].sum().sort_values(ascending=False).head(top_n)
        return [{"label": str(idx), "value": float(val)} for idx, val in grouped.items()]
    # fall back to counting rows if no numeric metric is mapped
    grouped = df[group_col].value_counts().head(top_n)
    return [{"label": str(idx), "value": int(val)} for idx, val in grouped.items()]


def business_insights(df: pd.DataFrame, mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
    insights: Dict[str, Any] = {}

    product_col, revenue_col, profit_col = mapping.get("product"), mapping.get("revenue"), mapping.get("profit")
    region_col = mapping.get("region")

    if product_col and revenue_col and product_col in df.columns and revenue_col in df.columns:
        by_product = df.groupby(product_col)[revenue_col].sum().sort_values(ascending=False)
        if len(by_product):
            insights["best_performing_product"] = str(by_product.index[0])
            insights["worst_performing_product"] = str(by_product.index[-1])

    if product_col and profit_col and product_col in df.columns and profit_col in df.columns:
        by_profit = df.groupby(product_col)[profit_col].sum().sort_values(ascending=False)
        if len(by_profit):
            insights["highest_profit_product"] = str(by_profit.index[0])
            loss_making = by_profit[by_profit < 0]
            insights["loss_making_products"] = [str(p) for p in loss_making.index.tolist()[:5]]

    if region_col and revenue_col and region_col in df.columns and revenue_col in df.columns:
        by_region = df.groupby(region_col)[revenue_col].sum().sort_values(ascending=False)
        if len(by_region):
            insights["top_region"] = str(by_region.index[0])
            insights["weak_region"] = str(by_region.index[-1])

    return insights
