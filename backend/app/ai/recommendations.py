"""
Rule-based recommendation engine.

Generates actionable business recommendations directly from computed
analytics (no LLM call needed, so this is fast and deterministic). These
rules encode common BI heuristics; thresholds can be tuned per business.
"""
from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from app.services.analytics import breakdown_by, business_insights, guess_column_mapping


def generate_recommendations(df: pd.DataFrame) -> List[str]:
    mapping = guess_column_mapping(list(df.columns))
    insights = business_insights(df, mapping)
    recommendations: List[str] = []

    if insights.get("best_performing_product"):
        recommendations.append(
            f"Increase inventory and marketing spend for '{insights['best_performing_product']}', "
            "your top revenue-generating product."
        )
    if insights.get("worst_performing_product"):
        recommendations.append(
            f"Consider discontinuing or discounting '{insights['worst_performing_product']}', "
            "which is underperforming relative to the rest of your catalog."
        )
    if insights.get("loss_making_products"):
        products = ", ".join(insights["loss_making_products"])
        recommendations.append(f"Review pricing or costs for loss-making products: {products}.")
    if insights.get("top_region"):
        recommendations.append(
            f"Double down on '{insights['top_region']}' with targeted campaigns — it's your strongest region."
        )
    if insights.get("weak_region"):
        recommendations.append(
            f"Investigate why '{insights['weak_region']}' is underperforming; consider localized promotions."
        )

    if not recommendations:
        recommendations.append(
            "Not enough recognizable columns (product/region/revenue) were found to generate "
            "specific recommendations. Try mapping columns manually via /analytics/mapping."
        )

    return recommendations
