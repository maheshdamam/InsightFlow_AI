from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    email: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    dataset_count: int = 0


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserActiveUpdate(BaseModel):
    is_active: bool


class AdminDatasetOut(BaseModel):
    id: str
    name: str
    owner_email: str
    row_count: int
    column_count: int
    status: str
    created_at: datetime


class ActivityLogOut(BaseModel):
    id: str
    action: str
    user_email: Optional[str] = None
    details: Dict[str, Any] = {}
    created_at: datetime


class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_datasets: int
    total_rows_ingested: int
    storage_bytes: int
    signups_last_7_days: int
    uploads_last_7_days: int
