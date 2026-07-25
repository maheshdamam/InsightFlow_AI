from sqlalchemy.orm import Session

from app.models.dataset import Dataset


def create_dataset(db: Session, **kwargs) -> Dataset:
    dataset = Dataset(**kwargs)
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def get_dataset(db: Session, dataset_id: str, owner_id: str) -> Dataset | None:
    return db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == owner_id).first()


def list_datasets(db: Session, owner_id: str):
    return db.query(Dataset).filter(Dataset.owner_id == owner_id).order_by(Dataset.created_at.desc()).all()


def rename_dataset(db: Session, dataset: Dataset, new_name: str) -> Dataset:
    dataset.name = new_name
    db.commit()
    db.refresh(dataset)
    return dataset


def delete_dataset(db: Session, dataset: Dataset) -> None:
    db.delete(dataset)
    db.commit()
