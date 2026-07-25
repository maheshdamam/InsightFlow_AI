"""
Small helper for reading/writing dataset files on disk.
Cleaned datasets are always persisted as parquet-free CSV for simplicity and
portability; the original upload is kept alongside for audit purposes.
"""
from __future__ import annotations

import os
import uuid

import pandas as pd

from app.config import settings


def read_upload_into_dataframe(file_bytes: bytes, filename: str) -> pd.DataFrame:
    import io

    if filename.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(file_bytes))
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
        except UnicodeDecodeError as e:
            last_error = e

    raise last_error


def save_cleaned_dataset(df: pd.DataFrame, dataset_id: str) -> str:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    path = os.path.join(settings.UPLOAD_DIR, f"{dataset_id}.csv")
    df.to_csv(path, index=False)
    return path


def load_cleaned_dataset(stored_path: str) -> pd.DataFrame:
    return pd.read_csv(stored_path)
