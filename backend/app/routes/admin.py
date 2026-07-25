import os
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.activity_log import list_recent_activity
from app.database import get_db
from app.models.activity_log import ActivityLog
from app.models.dataset import Dataset
from app.models.user import User, UserRole
from app.schemas.admin import (
    AdminDatasetOut,
    AdminUserOut,
    ActivityLogOut,
    SystemStats,
    UserActiveUpdate,
    UserRoleUpdate,
)
from app.utils.deps import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])

# Every route here requires the admin role
admin_only = require_role(UserRole.admin)


@router.get("/users", response_model=List[AdminUserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(admin_only)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    counts = dict(db.query(Dataset.owner_id, func.count(Dataset.id)).group_by(Dataset.owner_id).all())
    result = []
    for u in users:
        out = AdminUserOut.model_validate(u)
        out.dataset_count = counts.get(u.id, 0)
        result.append(out)
    return result


@router.patch("/users/{user_id}/role", response_model=AdminUserOut)
def update_user_role(
    user_id: str,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_only),
):
    if user_id == current_admin.id and payload.role != UserRole.admin:
        raise HTTPException(status_code=400, detail="You can't demote your own account")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = payload.role
    db.commit()
    db.refresh(user)
    out = AdminUserOut.model_validate(user)
    out.dataset_count = db.query(Dataset).filter(Dataset.owner_id == user.id).count()
    return out


@router.patch("/users/{user_id}/active", response_model=AdminUserOut)
def update_user_active(
    user_id: str,
    payload: UserActiveUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_only),
):
    if user_id == current_admin.id and not payload.is_active:
        raise HTTPException(status_code=400, detail="You can't deactivate your own account")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    out = AdminUserOut.model_validate(user)
    out.dataset_count = db.query(Dataset).filter(Dataset.owner_id == user.id).count()
    return out


@router.get("/datasets", response_model=List[AdminDatasetOut])
def list_all_datasets(db: Session = Depends(get_db), _: User = Depends(admin_only)):
    rows = (
        db.query(Dataset, User.email)
        .join(User, Dataset.owner_id == User.id)
        .order_by(Dataset.created_at.desc())
        .all()
    )
    return [
        AdminDatasetOut(
            id=ds.id,
            name=ds.name,
            owner_email=email,
            row_count=ds.row_count,
            column_count=ds.column_count,
            status=ds.status.value if hasattr(ds.status, "value") else str(ds.status),
            created_at=ds.created_at,
        )
        for ds, email in rows
    ]


@router.get("/activity", response_model=List[ActivityLogOut])
def get_activity_log(limit: int = 100, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    logs = list_recent_activity(db, limit=limit)
    return [
        ActivityLogOut(
            id=log.id,
            action=log.action,
            user_email=log.user.email if log.user else None,
            details=log.details or {},
            created_at=log.created_at,
        )
        for log in logs
    ]


@router.get("/stats", response_model=SystemStats)
def get_system_stats(db: Session = Depends(get_db), _: User = Depends(admin_only)):
    week_ago = datetime.utcnow() - timedelta(days=7)

    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active.is_(True)).count()
    total_datasets = db.query(Dataset).count()
    total_rows = db.query(func.coalesce(func.sum(Dataset.row_count), 0)).scalar() or 0
    signups_7d = db.query(User).filter(User.created_at >= week_ago).count()
    uploads_7d = (
        db.query(ActivityLog)
        .filter(ActivityLog.action == "dataset_uploaded", ActivityLog.created_at >= week_ago)
        .count()
    )

    # Storage: sum of file sizes for all stored dataset files (best-effort)
    storage_bytes = 0
    for (path,) in db.query(Dataset.stored_path).all():
        if path and os.path.exists(path):
            storage_bytes += os.path.getsize(path)

    return SystemStats(
        total_users=total_users,
        active_users=active_users,
        total_datasets=total_datasets,
        total_rows_ingested=int(total_rows),
        storage_bytes=storage_bytes,
        signups_last_7_days=signups_7d,
        uploads_last_7_days=uploads_7d,
    )
