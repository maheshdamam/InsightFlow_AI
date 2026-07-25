from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

from app.models.dataset import DatasetStatus


class DatasetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    original_filename: str
    version: int
    status: DatasetStatus
    row_count: int
    column_count: int
    column_schema: Dict[str, Any]
    cleaning_report: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class DatasetRename(BaseModel):
    name: str


class DatasetUploadResponse(BaseModel):
    dataset: DatasetOut
    message: str = "Dataset uploaded and cleaned successfully"
