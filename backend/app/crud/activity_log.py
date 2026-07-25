from typing import Optional

from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def log_activity(db: Session, action: str, user_id: Optional[str] = None, details: Optional[dict] = None) -> None:
    """Best-effort audit logging — never let a logging failure break the request it's logging."""
    try:
        entry = ActivityLog(user_id=user_id, action=action, details=details or {})
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()


def list_recent_activity(db: Session, limit: int = 100):
    return db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit).all()
