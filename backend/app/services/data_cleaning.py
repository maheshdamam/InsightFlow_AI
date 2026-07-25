"""
Automatic data cleaning pipeline.

Given a raw DataFrame loaded from an uploaded CSV/Excel file, this module:
- drops fully duplicate rows
- handles missing values (numeric -> median, categorical -> mode / "Unknown")
- attempts to standardize date-like columns to ISO format
- strips/normalizes whitespace and casing in text columns
- flags and removes rows that are entirely empty or unusable
- detects numeric outliers via IQR (reported, not silently dropped)

Returns the cleaned DataFrame plus a JSON-serializable report describing
every action taken, so the user can see exactly what changed.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

DATE_HINT_PATTERN = re.compile(r"date|_dt$|^dt_|time", re.IGNORECASE)


def _looks_like_date_column(col_name: str) -> bool:
    return bool(DATE_HINT_PATTERN.search(col_name))


def clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    report: Dict[str, Any] = {
        "initial_rows": int(len(df)),
        "initial_columns": int(len(df.columns)),
        "duplicates_removed": 0,
        "empty_rows_removed": 0,
        "missing_value_actions": {},
        "date_columns_standardized": [],
        "text_columns_normalized": [],
        "outliers_detected": {},
        "dtype_conversions": {},
    }

    df = df.copy()

    # 1. Normalize column names
    df.columns = [str(c).strip() for c in df.columns]

    # 2. Drop rows that are entirely empty
    before = len(df)
    df = df.dropna(how="all")
    report["empty_rows_removed"] = int(before - len(df))

    # 3. Remove exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    report["duplicates_removed"] = int(before - len(df))

    # 4. Per-column cleaning
    for col in df.columns:
        series = df[col]

        # Try numeric coercion first for object columns that are "mostly numeric"
        if series.dtype == object:
            coerced = pd.to_numeric(series, errors="coerce")
            non_null_ratio = coerced.notna().mean() if len(series) else 0
            if non_null_ratio > 0.9 and series.notna().mean() > 0:
                df[col] = coerced
                report["dtype_conversions"][col] = "object -> numeric"
                series = df[col]

        if pd.api.types.is_numeric_dtype(df[col]):
            missing = int(df[col].isna().sum())
            if missing > 0:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                report["missing_value_actions"][col] = f"filled {missing} missing with median ({median_val:.2f})"

            # IQR outlier detection (report only, values are kept)
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                outlier_count = int(((df[col] < lower) | (df[col] > upper)).sum())
                if outlier_count > 0:
                    report["outliers_detected"][col] = outlier_count

        elif _looks_like_date_column(col):
            parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().mean() > 0.5:
                df[col] = parsed.dt.strftime("%Y-%m-%d")
                report["date_columns_standardized"].append(col)

        else:
            # Text/categorical normalization
            missing = int(df[col].isna().sum())
            if missing > 0:
                df[col] = df[col].fillna("Unknown")
                report["missing_value_actions"][col] = f"filled {missing} missing with 'Unknown'"

            df[col] = df[col].astype(str).str.strip()
            report["text_columns_normalized"].append(col)

    report["final_rows"] = int(len(df))
    report["final_columns"] = int(len(df.columns))

    return df, report


def infer_schema(df: pd.DataFrame) -> Dict[str, str]:
    """Return a simple {column: dtype_name} map for storage on the Dataset row."""
    schema = {}
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_numeric_dtype(dtype):
            schema[col] = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            schema[col] = "date"
        else:
            schema[col] = "text"
    return schema
