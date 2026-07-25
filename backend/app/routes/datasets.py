from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.crud.dataset import (
    create_dataset,
    delete_dataset,
    get_dataset,
    list_datasets,
    rename_dataset,
)
from app.crud.activity_log import log_activity
from app.database import get_db
from app.models.dataset import DatasetStatus
from app.models.user import User
from app.schemas.dataset import DatasetOut, DatasetRename, DatasetUploadResponse
from app.services.analytics import guess_column_mapping
from app.services.data_cleaning import clean_dataframe, infer_schema
from app.services.dataset_io import read_upload_into_dataframe, save_cleaned_dataset
from app.ai.vector_store import index_dataset
from app.utils.deps import get_current_user

router = APIRouter(prefix="/datasets", tags=["Datasets"])

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE_MB = 200


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Use CSV or Excel.")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit")

    try:
        raw_df = read_upload_into_dataframe(file_bytes, file.filename)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse file: {exc}")

    if raw_df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file contains no data")

    cleaned_df, cleaning_report = clean_dataframe(raw_df)
    schema = infer_schema(cleaned_df)

    dataset = create_dataset(
        db,
        name=file.filename.rsplit(".", 1)[0],
        original_filename=file.filename,
        stored_path="",  # set after we know the dataset id
        status=DatasetStatus.ready,
        row_count=len(cleaned_df),
        column_count=len(cleaned_df.columns),
        column_schema=schema,
        cleaning_report=cleaning_report,
        owner_id=current_user.id,
    )

    stored_path = save_cleaned_dataset(cleaned_df, dataset.id)
    dataset.stored_path = stored_path
    db.commit()
    db.refresh(dataset)

    # Build the row-level retrieval index for the AI Copilot. Best-effort:
    # indexing failure shouldn't block the upload since the copilot still
    # works from stat-grounded context alone without it.
    try:
        mapping = guess_column_mapping(list(cleaned_df.columns))
        index_dataset(dataset.id, cleaned_df, mapping)
    except Exception:
        pass

    log_activity(
        db, "dataset_uploaded", user_id=current_user.id,
        details={"dataset_id": dataset.id, "name": dataset.name, "rows": dataset.row_count},
    )

    return DatasetUploadResponse(dataset=dataset)


@router.get("", response_model=list[DatasetOut])
def get_datasets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_datasets(db, current_user.id)


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset_detail(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = get_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.patch("/{dataset_id}", response_model=DatasetOut)
def rename_dataset_route(
    dataset_id: str,
    payload: DatasetRename,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = get_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return rename_dataset(db, dataset, payload.name)


@router.delete("/{dataset_id}", status_code=204)
def delete_dataset_route(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = get_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    log_activity(db, "dataset_deleted", user_id=current_user.id, details={"dataset_id": dataset.id, "name": dataset.name})
    delete_dataset(db, dataset)
