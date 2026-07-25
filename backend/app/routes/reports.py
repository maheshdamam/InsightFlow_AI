import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.crud.dataset import get_dataset
from app.database import get_db
from app.models.user import User
from app.services.dataset_io import load_cleaned_dataset
from app.services.reports import generate_excel_report, generate_pdf_report, generate_pptx_report
from app.utils.deps import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])

MEDIA_TYPES = {
    "pdf": "application/pdf",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def _load_dataset(dataset_id: str, db: Session, current_user: User):
    dataset = get_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = load_cleaned_dataset(dataset.stored_path)
    return dataset, df


@router.post("/{dataset_id}/pdf")
def export_pdf(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset, df = _load_dataset(dataset_id, db, current_user)
    path = generate_pdf_report(df, dataset.name, dataset.id)
    return FileResponse(path, media_type=MEDIA_TYPES["pdf"], filename=os.path.basename(path))


@router.post("/{dataset_id}/excel")
def export_excel(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset, df = _load_dataset(dataset_id, db, current_user)
    path = generate_excel_report(df, dataset.name, dataset.id)
    return FileResponse(path, media_type=MEDIA_TYPES["xlsx"], filename=os.path.basename(path))


@router.post("/{dataset_id}/powerpoint")
def export_pptx(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset, df = _load_dataset(dataset_id, db, current_user)
    path = generate_pptx_report(df, dataset.name, dataset.id)
    return FileResponse(path, media_type=MEDIA_TYPES["pptx"], filename=os.path.basename(path))
