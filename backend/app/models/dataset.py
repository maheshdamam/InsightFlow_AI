import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class DatasetStatus(str, enum.Enum):
    uploaded = "uploaded"
    cleaning = "cleaning"
    ready = "ready"
    failed = "failed"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    version = Column(Integer, default=1)
    status = Column(Enum(DatasetStatus), default=DatasetStatus.uploaded)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    column_schema = Column(JSON, default=dict)  # {column_name: dtype}
    cleaning_report = Column(JSON, default=dict)  # summary of cleaning actions taken
    owner_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="datasets")
